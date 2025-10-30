"""
Flask API for Multi-Factor Authentication System

RESTful API endpoints for enrollment, authentication, and system management.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
import bcrypt
from datetime import datetime, timedelta
import os
import sys
import numpy as np
import cv2
import base64
import json
from functools import wraps

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from biometrics.keystroke_dynamics import KeystrokeDynamicsAuth
from biometrics.face_recognition_module import FaceRecognitionAuth
from ml.classifiers import ScoreFusion
from utils.encryption import TemplateEncryption
from utils.database import Database
from utils.audit_logger import AuditLogger

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_EXPIRATION_HOURS'] = 24

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Initialize components
keystroke_auth = KeystrokeDynamicsAuth()
face_auth = FaceRecognitionAuth(model='hog', enable_liveness=True)
template_encryption = TemplateEncryption()
database = Database()
audit_logger = AuditLogger()


# Authentication decorator
def token_required(f):
    """Decorator to require JWT token for protected routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def generate_token(user_id: str) -> str:
    """Generate JWT token for user."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def decode_image(base64_string: str) -> np.ndarray:
    """Decode base64 image string to numpy array."""
    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    image_bytes = base64.b64decode(base64_string)
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


# User registration endpoint
@app.route('/api/register', methods=['POST'])
@limiter.limit("10 per hour")
def register_user():
    """
    Register a new user in the system.
    
    Expected JSON:
    {
        "user_id": "user123",
        "password": "secure_password",
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        password = data.get('password')
        email = data.get('email')
        
        if not user_id or not password:
            return jsonify({'error': 'user_id and password required'}), 400
        
        # Check if user exists
        if database.user_exists(user_id):
            return jsonify({'error': 'User already exists'}), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # Create user
        database.create_user(user_id, password_hash.decode(), email)
        
        # Log event
        audit_logger.log_event('user_registration', user_id, {'success': True})
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        audit_logger.log_event('user_registration', 'unknown', {
            'success': False,
            'error': str(e)
        })
        # Don't expose internal error details to users
        return jsonify({'error': 'Registration failed. Please try again.'}), 500


# Keystroke enrollment endpoint
@app.route('/api/enroll/keystroke', methods=['POST'])
@limiter.limit("20 per hour")
def enroll_keystroke():
    """
    Enroll user keystroke biometric.
    
    Expected JSON:
    {
        "user_id": "user123",
        "sessions": [
            [
                {"key": "a", "press_time": 0.0, "release_time": 0.1, "pressure": 0.5},
                {"key": "b", "press_time": 0.15, "release_time": 0.25, "pressure": 0.6},
                ...
            ],
            [...] // Multiple sessions
        ]
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        sessions = data.get('sessions')
        
        if not user_id or not sessions:
            return jsonify({'error': 'user_id and sessions required'}), 400
        
        if len(sessions) < 3:
            return jsonify({'error': 'At least 3 training sessions required'}), 400
        
        # Enroll user
        template = keystroke_auth.enroll_user(user_id, sessions)
        
        # Encrypt and save template
        template_dict = template.to_dict()
        encrypted_template = template_encryption.encrypt(json.dumps(template_dict))
        database.save_biometric_template(user_id, 'keystroke', encrypted_template)
        
        # Log event
        audit_logger.log_event('keystroke_enrollment', user_id, {
            'success': True,
            'num_sessions': len(sessions)
        })
        
        return jsonify({
            'message': 'Keystroke biometric enrolled successfully',
            'user_id': user_id,
            'num_samples': len(sessions)
        }), 201
        
    except Exception as e:
        audit_logger.log_event('keystroke_enrollment', user_id, {
            'success': False,
            'error': str(e)
        })
        # Don't expose internal error details to users
        return jsonify({'error': 'Enrollment failed. Please try again.'}), 500


# Face enrollment endpoint
@app.route('/api/enroll/face', methods=['POST'])
@limiter.limit("20 per hour")
def enroll_face():
    """
    Enroll user face biometric.
    
    Expected JSON:
    {
        "user_id": "user123",
        "images": ["base64_image1", "base64_image2", ...]
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        images_b64 = data.get('images')
        
        if not user_id or not images_b64:
            return jsonify({'error': 'user_id and images required'}), 400
        
        if len(images_b64) < 3:
            return jsonify({'error': 'At least 3 face images required'}), 400
        
        # Decode images
        images = []
        for img_b64 in images_b64:
            try:
                img = decode_image(img_b64)
                images.append(img)
            except Exception as e:
                print(f"Warning: Failed to decode image - {e}")
                continue
        
        if len(images) < 3:
            return jsonify({'error': 'At least 3 valid images required'}), 400
        
        # Enroll user
        template = face_auth.enroll_user(user_id, images)
        
        # Encrypt and save template
        template_dict = template.to_dict()
        encrypted_template = template_encryption.encrypt(json.dumps(template_dict))
        database.save_biometric_template(user_id, 'face', encrypted_template)
        
        # Log event
        audit_logger.log_event('face_enrollment', user_id, {
            'success': True,
            'num_images': len(images)
        })
        
        return jsonify({
            'message': 'Face biometric enrolled successfully',
            'user_id': user_id,
            'num_samples': len(images)
        }), 201
        
    except Exception as e:
        audit_logger.log_event('face_enrollment', user_id, {
            'success': False,
            'error': str(e)
        })
        # Don't expose internal error details to users
        return jsonify({'error': 'Enrollment failed. Please try again.'}), 500


# Keystroke authentication endpoint
@app.route('/api/authenticate/keystroke', methods=['POST'])
@limiter.limit("50 per hour")
def authenticate_keystroke():
    """
    Authenticate user with keystroke biometric.
    
    Expected JSON:
    {
        "user_id": "user123",
        "keystroke_data": [
            {"key": "a", "press_time": 0.0, "release_time": 0.1, "pressure": 0.5},
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        keystroke_data = data.get('keystroke_data')
        
        if not user_id or not keystroke_data:
            return jsonify({'error': 'user_id and keystroke_data required'}), 400
        
        # Load template
        encrypted_template = database.get_biometric_template(user_id, 'keystroke')
        if not encrypted_template:
            return jsonify({'error': 'User not enrolled'}), 404
        
        template_dict = json.loads(template_encryption.decrypt(encrypted_template))
        keystroke_auth.templates[user_id] = keystroke_auth.feature_extractor.__class__
        # For simplicity, we'll re-create the template object
        from biometrics.keystroke_dynamics import KeystrokeTemplate
        template = KeystrokeTemplate.from_dict(template_dict)
        keystroke_auth.templates[user_id] = template
        
        # Authenticate
        is_authenticated, score, details = keystroke_auth.authenticate(
            user_id, keystroke_data
        )
        
        # Log event
        audit_logger.log_event('keystroke_authentication', user_id, {
            'success': is_authenticated,
            'score': score
        })
        
        response = {
            'authenticated': is_authenticated,
            'score': score,
            'modality': 'keystroke',
            'details': details
        }
        
        if is_authenticated:
            response['token'] = generate_token(user_id)
        
        return jsonify(response), 200
        
    except Exception as e:
        audit_logger.log_event('keystroke_authentication', user_id, {
            'success': False,
            'error': str(e)
        })
        # Don't expose internal error details to users
        return jsonify({'error': 'Authentication failed. Please try again.'}), 500


# Face authentication endpoint
@app.route('/api/authenticate/face', methods=['POST'])
@limiter.limit("50 per hour")
def authenticate_face():
    """
    Authenticate user with face biometric.
    
    Expected JSON:
    {
        "user_id": "user123",
        "image": "base64_image"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        image_b64 = data.get('image')
        
        if not user_id or not image_b64:
            return jsonify({'error': 'user_id and image required'}), 400
        
        # Load template
        encrypted_template = database.get_biometric_template(user_id, 'face')
        if not encrypted_template:
            return jsonify({'error': 'User not enrolled'}), 404
        
        template_dict = json.loads(template_encryption.decrypt(encrypted_template))
        from biometrics.face_recognition_module import FaceTemplate
        template = FaceTemplate.from_dict(template_dict)
        face_auth.templates[user_id] = template
        
        # Decode image
        image = decode_image(image_b64)
        
        # Authenticate
        is_authenticated, score, details = face_auth.authenticate(user_id, image)
        
        # Log event
        audit_logger.log_event('face_authentication', user_id, {
            'success': is_authenticated,
            'score': score,
            'liveness_passed': details.get('liveness_score', 0) > 0.5
        })
        
        response = {
            'authenticated': is_authenticated,
            'score': score,
            'modality': 'face',
            'details': details
        }
        
        if is_authenticated:
            response['token'] = generate_token(user_id)
        
        return jsonify(response), 200
        
    except Exception as e:
        audit_logger.log_event('face_authentication', user_id, {
            'success': False,
            'error': str(e)
        })
        # Don't expose internal error details to users
        return jsonify({'error': 'Authentication failed. Please try again.'}), 500


# Multi-factor authentication endpoint
@app.route('/api/authenticate/mfa', methods=['POST'])
@limiter.limit("30 per hour")
def authenticate_mfa():
    """
    Authenticate user with multiple biometric factors.
    
    Expected JSON:
    {
        "user_id": "user123",
        "keystroke_data": [...],
        "face_image": "base64_image",
        "fusion_method": "weighted_sum"  // optional
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        keystroke_data = data.get('keystroke_data')
        face_image_b64 = data.get('face_image')
        fusion_method = data.get('fusion_method', 'weighted_sum')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        scores = []
        decisions = []
        details_list = []
        
        # Keystroke authentication
        if keystroke_data:
            encrypted_template = database.get_biometric_template(user_id, 'keystroke')
            if encrypted_template:
                template_dict = json.loads(template_encryption.decrypt(encrypted_template))
                from biometrics.keystroke_dynamics import KeystrokeTemplate
                template = KeystrokeTemplate.from_dict(template_dict)
                keystroke_auth.templates[user_id] = template
                
                is_auth, score, details = keystroke_auth.authenticate(user_id, keystroke_data)
                scores.append(score)
                decisions.append(is_auth)
                details_list.append({'modality': 'keystroke', **details})
        
        # Face authentication
        if face_image_b64:
            encrypted_template = database.get_biometric_template(user_id, 'face')
            if encrypted_template:
                template_dict = json.loads(template_encryption.decrypt(encrypted_template))
                from biometrics.face_recognition_module import FaceTemplate
                template = FaceTemplate.from_dict(template_dict)
                face_auth.templates[user_id] = template
                
                image = decode_image(face_image_b64)
                is_auth, score, details = face_auth.authenticate(user_id, image)
                scores.append(score)
                decisions.append(is_auth)
                details_list.append({'modality': 'face', **details})
        
        if len(scores) == 0:
            return jsonify({'error': 'No biometric data provided'}), 400
        
        # Fusion
        if fusion_method == 'weighted_sum':
            # Weight face more heavily (0.6) than keystroke (0.4)
            weights = [0.4, 0.6] if len(scores) == 2 else [1.0]
            fused_score = ScoreFusion.simple_sum(scores, weights)
        elif fusion_method == 'product':
            fused_score = ScoreFusion.product_rule(scores)
        elif fusion_method == 'mean':
            fused_score = ScoreFusion.mean_rule(scores)
        else:
            fused_score = ScoreFusion.simple_sum(scores)
        
        # Decision fusion (require both to pass if both provided)
        is_authenticated = ScoreFusion.decision_level_fusion(decisions, strategy='and')
        
        # Log event
        audit_logger.log_event('mfa_authentication', user_id, {
            'success': is_authenticated,
            'fused_score': fused_score,
            'num_modalities': len(scores)
        })
        
        response = {
            'authenticated': is_authenticated,
            'fused_score': fused_score,
            'individual_scores': scores,
            'details': details_list
        }
        
        if is_authenticated:
            response['token'] = generate_token(user_id)
        
        return jsonify(response), 200
        
    except Exception as e:
        audit_logger.log_event('mfa_authentication', user_id, {
            'success': False,
            'error': str(e)
        })
        # Don't expose internal error details to users
        return jsonify({'error': 'Authentication failed. Please try again.'}), 500


# System metrics endpoint
@app.route('/api/metrics', methods=['GET'])
@token_required
def get_system_metrics(current_user):
    """Get system performance metrics."""
    try:
        metrics = database.get_system_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        # Don't expose internal error details to users
        return jsonify({'error': 'Failed to retrieve metrics.'}), 500


# User status endpoint
@app.route('/api/user/<user_id>/status', methods=['GET'])
@token_required
def get_user_status(current_user, user_id):
    """Get user enrollment status."""
    try:
        if current_user != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        keystroke_enrolled = database.get_biometric_template(user_id, 'keystroke') is not None
        face_enrolled = database.get_biometric_template(user_id, 'face') is not None
        
        return jsonify({
            'user_id': user_id,
            'keystroke_enrolled': keystroke_enrolled,
            'face_enrolled': face_enrolled,
            'mfa_enabled': keystroke_enrolled and face_enrolled
        }), 200
        
    except Exception as e:
        # Don't expose internal error details to users
        return jsonify({'error': 'Failed to retrieve user status.'}), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('storage/templates', exist_ok=True)
    os.makedirs('storage/logs', exist_ok=True)
    
    # Run app (debug mode from environment variable, defaults to False for security)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
