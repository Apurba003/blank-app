"""
Face Recognition Biometric Authentication Module

This module implements face recognition with anti-spoofing and liveness detection.
"""

import numpy as np
import cv2
import face_recognition
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime


class FaceFeatureExtractor:
    """
    Extracts facial features and embeddings for authentication.
    """
    
    def __init__(self, model: str = 'hog'):
        """
        Initialize face feature extractor.
        
        Args:
            model: 'hog' for CPU, 'cnn' for GPU (more accurate but slower)
        """
        self.model = model
        
    def detect_faces(self, image: np.ndarray) -> List[Tuple]:
        """
        Detect faces in an image.
        
        Args:
            image: Image array (BGR or RGB)
            
        Returns:
            List of face locations (top, right, bottom, left)
        """
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
            
        face_locations = face_recognition.face_locations(rgb_image, model=self.model)
        return face_locations
    
    def extract_landmarks(self, image: np.ndarray, face_locations: List[Tuple]) -> List[Dict]:
        """
        Extract facial landmarks.
        
        Args:
            image: Image array
            face_locations: List of face locations
            
        Returns:
            List of landmark dictionaries
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        landmarks_list = face_recognition.face_landmarks(rgb_image, face_locations)
        return landmarks_list
    
    def extract_encoding(self, image: np.ndarray, face_location: Tuple = None) -> np.ndarray:
        """
        Extract 128-dimensional face encoding (embedding).
        
        Args:
            image: Image array
            face_location: Optional specific face location
            
        Returns:
            128-dimensional face encoding
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if face_location:
            encodings = face_recognition.face_encodings(rgb_image, [face_location])
        else:
            encodings = face_recognition.face_encodings(rgb_image)
        
        if len(encodings) == 0:
            raise ValueError("No face found in image")
        
        return encodings[0]
    
    def compute_geometric_features(self, landmarks: Dict) -> np.ndarray:
        """
        Compute geometric features from facial landmarks.
        
        Args:
            landmarks: Dictionary of facial landmarks
            
        Returns:
            Geometric feature vector
        """
        features = []
        
        # Extract key landmark points
        left_eye = np.array(landmarks.get('left_eye', []))
        right_eye = np.array(landmarks.get('right_eye', []))
        nose_bridge = np.array(landmarks.get('nose_bridge', []))
        nose_tip = np.array(landmarks.get('nose_tip', []))
        chin = np.array(landmarks.get('chin', []))
        
        # Calculate distances and ratios
        if len(left_eye) > 0 and len(right_eye) > 0:
            # Eye distance
            left_eye_center = np.mean(left_eye, axis=0)
            right_eye_center = np.mean(right_eye, axis=0)
            eye_distance = np.linalg.norm(left_eye_center - right_eye_center)
            features.append(eye_distance)
        
        if len(nose_bridge) > 0 and len(chin) > 0:
            # Face height
            nose_top = nose_bridge[0]
            chin_bottom = chin[len(chin) // 2]
            face_height = np.linalg.norm(nose_top - chin_bottom)
            features.append(face_height)
        
        if len(nose_tip) > 0 and len(chin) > 0:
            # Nose-chin distance
            nose_center = np.mean(nose_tip, axis=0)
            chin_center = np.mean(chin, axis=0)
            nose_chin_dist = np.linalg.norm(nose_center - chin_center)
            features.append(nose_chin_dist)
        
        return np.array(features) if features else np.zeros(3)


class LivenessDetector:
    """
    Implements anti-spoofing and liveness detection.
    """
    
    def __init__(self):
        self.blink_threshold = 0.2
        self.eye_aspect_ratio_threshold = 0.25
    
    def detect_blink(self, landmarks: Dict) -> bool:
        """
        Detect eye blink from landmarks.
        
        Args:
            landmarks: Facial landmarks dictionary
            
        Returns:
            True if blink detected
        """
        left_eye = landmarks.get('left_eye', [])
        right_eye = landmarks.get('right_eye', [])
        
        if not left_eye or not right_eye:
            return False
        
        # Calculate eye aspect ratio (EAR)
        def eye_aspect_ratio(eye):
            eye = np.array(eye)
            if len(eye) < 6:
                return 1.0
            
            # Vertical distances
            v1 = np.linalg.norm(eye[1] - eye[5])
            v2 = np.linalg.norm(eye[2] - eye[4])
            
            # Horizontal distance
            h = np.linalg.norm(eye[0] - eye[3])
            
            ear = (v1 + v2) / (2.0 * h)
            return ear
        
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        return avg_ear < self.eye_aspect_ratio_threshold
    
    def detect_texture(self, image: np.ndarray, face_location: Tuple) -> float:
        """
        Analyze image texture to detect printed photos or screens.
        
        Args:
            image: Image array
            face_location: Face bounding box
            
        Returns:
            Liveness score (0-1, higher is more likely real)
        """
        top, right, bottom, left = face_location
        face_region = image[top:bottom, left:right]
        
        if face_region.size == 0:
            return 0.0
        
        # Convert to grayscale
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance (focus measure)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate local binary pattern variance
        lbp_var = self._calculate_lbp_variance(gray)
        
        # Combine metrics
        texture_score = min(1.0, (laplacian_var / 100.0 + lbp_var / 50.0) / 2.0)
        
        return texture_score
    
    def _calculate_lbp_variance(self, gray_image: np.ndarray) -> float:
        """Calculate variance of Local Binary Pattern."""
        height, width = gray_image.shape
        if height < 3 or width < 3:
            return 0.0
        
        # Simple LBP calculation
        lbp = np.zeros((height - 2, width - 2))
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                center = gray_image[i, j]
                code = 0
                code |= (gray_image[i-1, j-1] > center) << 7
                code |= (gray_image[i-1, j] > center) << 6
                code |= (gray_image[i-1, j+1] > center) << 5
                code |= (gray_image[i, j+1] > center) << 4
                code |= (gray_image[i+1, j+1] > center) << 3
                code |= (gray_image[i+1, j] > center) << 2
                code |= (gray_image[i+1, j-1] > center) << 1
                code |= (gray_image[i, j-1] > center) << 0
                lbp[i-1, j-1] = code
        
        return float(np.var(lbp))
    
    def check_liveness(self, image: np.ndarray, face_location: Tuple, 
                      landmarks: Dict = None) -> Tuple[bool, float, Dict]:
        """
        Comprehensive liveness check.
        
        Args:
            image: Image array
            face_location: Face bounding box
            landmarks: Optional facial landmarks
            
        Returns:
            Tuple of (is_live, confidence, details)
        """
        details = {}
        
        # Texture analysis
        texture_score = self.detect_texture(image, face_location)
        details['texture_score'] = float(texture_score)
        
        # Blink detection (if landmarks provided)
        if landmarks:
            blink_detected = self.detect_blink(landmarks)
            details['blink_detected'] = blink_detected
        else:
            blink_detected = False
            details['blink_detected'] = None
        
        # Overall liveness score
        liveness_score = texture_score
        if landmarks:
            liveness_score = (texture_score + (0.3 if blink_detected else 0.0)) / 1.3
        
        is_live = liveness_score > 0.5
        
        details['liveness_score'] = float(liveness_score)
        
        return is_live, liveness_score, details


class FaceTemplate:
    """
    Manages face biometric templates for users.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.encodings = []
        self.template = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_encoding(self, encoding: np.ndarray):
        """Add a face encoding sample."""
        self.encodings.append(encoding)
        self.updated_at = datetime.now()
    
    def create_template(self, min_samples: int = 3):
        """
        Create template from collected encodings.
        
        Args:
            min_samples: Minimum number of samples required
        """
        if len(self.encodings) < min_samples:
            raise ValueError(f"Need at least {min_samples} samples, got {len(self.encodings)}")
        
        # Calculate mean encoding
        encodings_array = np.array(self.encodings)
        self.template = {
            'mean_encoding': np.mean(encodings_array, axis=0),
            'std': np.std(encodings_array, axis=0),
            'num_samples': len(self.encodings)
        }
        self.updated_at = datetime.now()
        
        return self.template
    
    def verify(self, encoding: np.ndarray, tolerance: float = 0.6) -> Tuple[bool, float]:
        """
        Verify if encoding matches this template.
        
        Args:
            encoding: Face encoding to verify
            tolerance: Distance threshold (lower is stricter)
            
        Returns:
            Tuple of (is_match, similarity_score)
        """
        if self.template is None:
            raise ValueError("Template not created yet")
        
        mean_encoding = self.template['mean_encoding']
        
        # Calculate Euclidean distance
        distance = np.linalg.norm(encoding - mean_encoding)
        
        # Calculate similarity score (0-1, higher is better)
        similarity = 1.0 / (1.0 + distance)
        
        # Verify against tolerance
        is_match = distance <= tolerance
        
        return is_match, similarity
    
    def to_dict(self) -> Dict:
        """Convert template to dictionary for storage."""
        return {
            'user_id': self.user_id,
            'template': {
                'mean_encoding': self.template['mean_encoding'].tolist() if self.template else None,
                'std': self.template['std'].tolist() if self.template else None,
                'num_samples': self.template['num_samples'] if self.template else 0
            } if self.template else None,
            'num_encodings': len(self.encodings),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FaceTemplate':
        """Create template from dictionary."""
        template = cls(data['user_id'])
        template.created_at = datetime.fromisoformat(data['created_at'])
        template.updated_at = datetime.fromisoformat(data['updated_at'])
        
        if data['template']:
            template.template = {
                'mean_encoding': np.array(data['template']['mean_encoding']),
                'std': np.array(data['template']['std']),
                'num_samples': data['template']['num_samples']
            }
        
        return template


class FaceRecognitionAuth:
    """
    Main face recognition authentication system.
    """
    
    def __init__(self, model: str = 'hog', enable_liveness: bool = True):
        """
        Initialize face recognition system.
        
        Args:
            model: Face detection model ('hog' or 'cnn')
            enable_liveness: Enable liveness detection
        """
        self.feature_extractor = FaceFeatureExtractor(model)
        self.liveness_detector = LivenessDetector() if enable_liveness else None
        self.templates = {}
        self.enable_liveness = enable_liveness
    
    def enroll_user(self, user_id: str, images: List[np.ndarray]) -> FaceTemplate:
        """
        Enroll a user with multiple face images.
        
        Args:
            user_id: User identifier
            images: List of face images
            
        Returns:
            Created template
        """
        template = FaceTemplate(user_id)
        
        for image in images:
            try:
                encoding = self.feature_extractor.extract_encoding(image)
                template.add_encoding(encoding)
            except ValueError as e:
                print(f"Warning: Skipping image - {e}")
                continue
        
        if len(template.encodings) == 0:
            raise ValueError("No valid face encodings extracted from images")
        
        template.create_template()
        self.templates[user_id] = template
        
        return template
    
    def authenticate(self, user_id: str, image: np.ndarray, 
                    tolerance: float = 0.6) -> Tuple[bool, float, Dict]:
        """
        Authenticate a user based on face recognition.
        
        Args:
            user_id: User identifier
            image: Face image
            tolerance: Verification tolerance
            
        Returns:
            Tuple of (is_authenticated, score, details)
        """
        if user_id not in self.templates:
            return False, 0.0, {'error': 'User not enrolled'}
        
        try:
            # Detect face
            face_locations = self.feature_extractor.detect_faces(image)
            
            if len(face_locations) == 0:
                return False, 0.0, {'error': 'No face detected'}
            
            if len(face_locations) > 1:
                return False, 0.0, {'error': 'Multiple faces detected'}
            
            face_location = face_locations[0]
            
            # Liveness check
            details = {'liveness_check': False}
            if self.enable_liveness:
                landmarks_list = self.feature_extractor.extract_landmarks(image, [face_location])
                landmarks = landmarks_list[0] if landmarks_list else None
                
                is_live, liveness_score, liveness_details = self.liveness_detector.check_liveness(
                    image, face_location, landmarks
                )
                
                details.update(liveness_details)
                details['liveness_check'] = True
                
                if not is_live:
                    return False, 0.0, {**details, 'error': 'Liveness check failed'}
            
            # Extract encoding
            encoding = self.feature_extractor.extract_encoding(image, face_location)
            
            # Verify against template
            template = self.templates[user_id]
            is_match, score = template.verify(encoding, tolerance)
            
            details.update({
                'score': float(score),
                'tolerance': tolerance,
                'timestamp': datetime.now().isoformat()
            })
            
            return is_match, score, details
            
        except Exception as e:
            return False, 0.0, {'error': str(e)}
    
    def get_template(self, user_id: str) -> FaceTemplate:
        """Get template for a user."""
        return self.templates.get(user_id)
    
    def save_template(self, user_id: str, filepath: str):
        """Save template to file."""
        if user_id not in self.templates:
            raise ValueError(f"User {user_id} not found")
        
        with open(filepath, 'w') as f:
            json.dump(self.templates[user_id].to_dict(), f, indent=2)
    
    def load_template(self, filepath: str):
        """Load template from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        template = FaceTemplate.from_dict(data)
        self.templates[template.user_id] = template
