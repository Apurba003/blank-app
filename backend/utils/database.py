"""
Database Module

Simple file-based storage for biometric templates and user data.
In production, replace with SQLAlchemy/PostgreSQL.
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional
import threading


class Database:
    """
    Simple file-based database for storing user data and biometric templates.
    """
    
    def __init__(self, storage_path: str = 'storage'):
        """
        Initialize database.
        
        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = storage_path
        self.users_file = os.path.join(storage_path, 'users.json')
        self.templates_dir = os.path.join(storage_path, 'templates')
        self.metrics_file = os.path.join(storage_path, 'metrics.json')
        
        # Create directories
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Thread lock for file operations
        self.lock = threading.Lock()
        
        # Initialize files
        self._init_files()
    
    def _init_files(self):
        """Initialize database files if they don't exist."""
        if not os.path.exists(self.users_file):
            self._save_json(self.users_file, {})
        
        if not os.path.exists(self.metrics_file):
            self._save_json(self.metrics_file, {
                'total_users': 0,
                'total_authentications': 0,
                'successful_authentications': 0,
                'failed_authentications': 0,
                'enrollments': {
                    'keystroke': 0,
                    'face': 0
                }
            })
    
    def _load_json(self, filepath: str) -> Dict:
        """Load JSON file."""
        with self.lock:
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {}
    
    def _save_json(self, filepath: str, data: Dict):
        """Save JSON file."""
        with self.lock:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user exists."""
        users = self._load_json(self.users_file)
        return user_id in users
    
    def create_user(self, user_id: str, password_hash: str, email: str = None):
        """
        Create a new user.
        
        Args:
            user_id: User identifier
            password_hash: Hashed password
            email: User email
        """
        users = self._load_json(self.users_file)
        
        if user_id in users:
            raise ValueError(f"User {user_id} already exists")
        
        users[user_id] = {
            'password_hash': password_hash,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self._save_json(self.users_file, users)
        
        # Update metrics
        metrics = self._load_json(self.metrics_file)
        metrics['total_users'] = metrics.get('total_users', 0) + 1
        self._save_json(self.metrics_file, metrics)
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user data."""
        users = self._load_json(self.users_file)
        return users.get(user_id)
    
    def verify_password(self, user_id: str, password: str) -> bool:
        """Verify user password."""
        import bcrypt
        user = self.get_user(user_id)
        if not user:
            return False
        
        password_hash = user['password_hash'].encode()
        return bcrypt.checkpw(password.encode(), password_hash)
    
    def save_biometric_template(self, user_id: str, modality: str, 
                               encrypted_template: str):
        """
        Save encrypted biometric template.
        
        Args:
            user_id: User identifier
            modality: 'keystroke' or 'face'
            encrypted_template: Encrypted template data
        """
        template_file = os.path.join(
            self.templates_dir, 
            f"{user_id}_{modality}.json"
        )
        
        template_data = {
            'user_id': user_id,
            'modality': modality,
            'encrypted_template': encrypted_template,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self._save_json(template_file, template_data)
        
        # Update metrics
        metrics = self._load_json(self.metrics_file)
        if 'enrollments' not in metrics:
            metrics['enrollments'] = {}
        metrics['enrollments'][modality] = metrics['enrollments'].get(modality, 0) + 1
        self._save_json(self.metrics_file, metrics)
    
    def get_biometric_template(self, user_id: str, modality: str) -> Optional[str]:
        """
        Get encrypted biometric template.
        
        Args:
            user_id: User identifier
            modality: 'keystroke' or 'face'
            
        Returns:
            Encrypted template data or None
        """
        template_file = os.path.join(
            self.templates_dir, 
            f"{user_id}_{modality}.json"
        )
        
        if not os.path.exists(template_file):
            return None
        
        template_data = self._load_json(template_file)
        return template_data.get('encrypted_template')
    
    def record_authentication(self, user_id: str, success: bool, modality: str):
        """
        Record an authentication attempt.
        
        Args:
            user_id: User identifier
            success: Whether authentication was successful
            modality: Authentication modality
        """
        metrics = self._load_json(self.metrics_file)
        
        metrics['total_authentications'] = metrics.get('total_authentications', 0) + 1
        
        if success:
            metrics['successful_authentications'] = metrics.get('successful_authentications', 0) + 1
        else:
            metrics['failed_authentications'] = metrics.get('failed_authentications', 0) + 1
        
        self._save_json(self.metrics_file, metrics)
    
    def get_system_metrics(self) -> Dict:
        """Get system metrics."""
        metrics = self._load_json(self.metrics_file)
        
        # Calculate success rate
        total = metrics.get('total_authentications', 0)
        successful = metrics.get('successful_authentications', 0)
        
        if total > 0:
            success_rate = successful / total
        else:
            success_rate = 0.0
        
        metrics['success_rate'] = success_rate
        
        return metrics
