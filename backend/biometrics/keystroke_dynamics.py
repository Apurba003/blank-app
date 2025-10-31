"""
Keystroke Dynamics Biometric Authentication Module

This module implements keystroke dynamics authentication with feature extraction,
statistical analysis, and template management.
"""

import numpy as np
from typing import List, Dict, Tuple
import json
from datetime import datetime


class KeystrokeFeatureExtractor:
    """
    Extracts biometric features from keystroke timing patterns.
    
    Features extracted:
    - Dwell time: Time a key is held down
    - Flight time: Time between key releases and next key press
    - Pressure: Simulated pressure/typing strength
    """
    
    def __init__(self):
        self.feature_names = []
        
    def extract_features(self, keystroke_data: List[Dict]) -> np.ndarray:
        """
        Extract statistical features from keystroke timing data.
        
        Args:
            keystroke_data: List of dicts with 'key', 'press_time', 'release_time', 'pressure'
            
        Returns:
            Feature vector as numpy array
        """
        if len(keystroke_data) < 2:
            raise ValueError("Need at least 2 keystrokes for feature extraction")
            
        # Extract raw timing features
        dwell_times = []
        flight_times = []
        pressures = []
        
        for i, keystroke in enumerate(keystroke_data):
            # Dwell time: time key is held down
            dwell_time = keystroke['release_time'] - keystroke['press_time']
            dwell_times.append(dwell_time)
            
            # Pressure (if available)
            pressure = keystroke.get('pressure', 0.5)
            pressures.append(pressure)
            
            # Flight time: time between current release and next press
            if i < len(keystroke_data) - 1:
                flight_time = keystroke_data[i + 1]['press_time'] - keystroke['release_time']
                flight_times.append(flight_time)
        
        # Calculate statistical features
        features = []
        
        # Dwell time statistics
        features.extend([
            np.mean(dwell_times),
            np.std(dwell_times),
            np.var(dwell_times),
            np.median(dwell_times),
            np.min(dwell_times),
            np.max(dwell_times)
        ])
        
        # Flight time statistics
        if flight_times:
            features.extend([
                np.mean(flight_times),
                np.std(flight_times),
                np.var(flight_times),
                np.median(flight_times),
                np.min(flight_times),
                np.max(flight_times)
            ])
        else:
            features.extend([0, 0, 0, 0, 0, 0])
        
        # Pressure statistics
        features.extend([
            np.mean(pressures),
            np.std(pressures),
            np.var(pressures)
        ])
        
        # Typing rhythm features
        if len(dwell_times) > 1:
            features.extend([
                np.mean(np.diff(dwell_times)),  # Dwell time variation
                np.std(np.diff(dwell_times))
            ])
        else:
            features.extend([0, 0])
            
        if len(flight_times) > 1:
            features.extend([
                np.mean(np.diff(flight_times)),  # Flight time variation
                np.std(np.diff(flight_times))
            ])
        else:
            features.extend([0, 0])
        
        return np.array(features)
    
    def extract_digraph_features(self, keystroke_data: List[Dict]) -> Dict[str, float]:
        """
        Extract digraph (two-key combination) timing features.
        
        Args:
            keystroke_data: List of keystroke events
            
        Returns:
            Dictionary of digraph features
        """
        digraphs = {}
        
        for i in range(len(keystroke_data) - 1):
            key1 = keystroke_data[i]['key']
            key2 = keystroke_data[i + 1]['key']
            digraph = f"{key1}-{key2}"
            
            # Calculate digraph timing
            timing = keystroke_data[i + 1]['press_time'] - keystroke_data[i]['press_time']
            
            if digraph not in digraphs:
                digraphs[digraph] = []
            digraphs[digraph].append(timing)
        
        # Calculate statistics for each digraph
        digraph_features = {}
        for digraph, timings in digraphs.items():
            digraph_features[f"{digraph}_mean"] = np.mean(timings)
            digraph_features[f"{digraph}_std"] = np.std(timings)
        
        return digraph_features


class KeystrokeTemplate:
    """
    Manages keystroke biometric templates for users.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.samples = []
        self.template = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_sample(self, features: np.ndarray):
        """Add a training sample to the template."""
        self.samples.append(features)
        self.updated_at = datetime.now()
    
    def create_template(self, min_samples: int = 5):
        """
        Create a template from collected samples.
        
        Args:
            min_samples: Minimum number of samples required
        """
        if len(self.samples) < min_samples:
            raise ValueError(f"Need at least {min_samples} samples, got {len(self.samples)}")
        
        # Calculate mean and std for each feature
        samples_array = np.array(self.samples)
        self.template = {
            'mean': np.mean(samples_array, axis=0),
            'std': np.std(samples_array, axis=0),
            'min': np.min(samples_array, axis=0),
            'max': np.max(samples_array, axis=0),
            'num_samples': len(self.samples)
        }
        self.updated_at = datetime.now()
        
        return self.template
    
    def verify(self, features: np.ndarray, threshold: float = 3.0) -> Tuple[bool, float]:
        """
        Verify if features match this template.
        
        Args:
            features: Feature vector to verify
            threshold: Number of standard deviations for acceptance
            
        Returns:
            Tuple of (is_genuine, similarity_score)
        """
        if self.template is None:
            raise ValueError("Template not created yet")
        
        mean = self.template['mean']
        std = self.template['std']
        
        # Calculate Mahalanobis-like distance
        # Avoid division by zero
        std_safe = np.where(std == 0, 1e-10, std)
        normalized_diff = (features - mean) / std_safe
        distance = np.sqrt(np.sum(normalized_diff ** 2))
        
        # Calculate similarity score (0-1, higher is better)
        similarity = 1.0 / (1.0 + distance)
        
        # Verify against threshold
        is_genuine = distance < threshold * np.sqrt(len(features))
        
        return is_genuine, similarity
    
    def to_dict(self) -> Dict:
        """Convert template to dictionary for storage."""
        return {
            'user_id': self.user_id,
            'template': {
                'mean': self.template['mean'].tolist() if self.template else None,
                'std': self.template['std'].tolist() if self.template else None,
                'min': self.template['min'].tolist() if self.template else None,
                'max': self.template['max'].tolist() if self.template else None,
                'num_samples': self.template['num_samples'] if self.template else 0
            } if self.template else None,
            'num_samples': len(self.samples),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'KeystrokeTemplate':
        """Create template from dictionary."""
        template = cls(data['user_id'])
        template.created_at = datetime.fromisoformat(data['created_at'])
        template.updated_at = datetime.fromisoformat(data['updated_at'])
        
        if data['template']:
            template.template = {
                'mean': np.array(data['template']['mean']),
                'std': np.array(data['template']['std']),
                'min': np.array(data['template']['min']),
                'max': np.array(data['template']['max']),
                'num_samples': data['template']['num_samples']
            }
        
        return template


class KeystrokeDynamicsAuth:
    """
    Main keystroke dynamics authentication system.
    """
    
    def __init__(self):
        self.feature_extractor = KeystrokeFeatureExtractor()
        self.templates = {}
    
    def enroll_user(self, user_id: str, sessions: List[List[Dict]]) -> KeystrokeTemplate:
        """
        Enroll a user with multiple typing sessions.
        
        Args:
            user_id: User identifier
            sessions: List of typing sessions, each session is a list of keystroke events
            
        Returns:
            Created template
        """
        template = KeystrokeTemplate(user_id)
        
        for session in sessions:
            features = self.feature_extractor.extract_features(session)
            template.add_sample(features)
        
        template.create_template()
        self.templates[user_id] = template
        
        return template
    
    def authenticate(self, user_id: str, keystroke_data: List[Dict], 
                    threshold: float = 3.0) -> Tuple[bool, float, Dict]:
        """
        Authenticate a user based on keystroke dynamics.
        
        Args:
            user_id: User identifier
            keystroke_data: List of keystroke events
            threshold: Verification threshold
            
        Returns:
            Tuple of (is_authenticated, score, details)
        """
        if user_id not in self.templates:
            return False, 0.0, {'error': 'User not enrolled'}
        
        try:
            features = self.feature_extractor.extract_features(keystroke_data)
            template = self.templates[user_id]
            is_genuine, score = template.verify(features, threshold)
            
            details = {
                'score': float(score),
                'threshold': threshold,
                'num_keystrokes': len(keystroke_data),
                'timestamp': datetime.now().isoformat()
            }
            
            return is_genuine, score, details
            
        except Exception as e:
            return False, 0.0, {'error': str(e)}
    
    def get_template(self, user_id: str) -> KeystrokeTemplate:
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
        
        template = KeystrokeTemplate.from_dict(data)
        self.templates[template.user_id] = template
