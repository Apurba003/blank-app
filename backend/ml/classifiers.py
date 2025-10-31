"""
Classifiers and Performance Metrics

Implements SVM, Random Forest classifiers and biometric performance metrics
(FAR, FRR, EER).
"""

import numpy as np
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from typing import Tuple, Dict, List
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from scipy.interpolate import interp1d


class BiometricClassifier:
    """
    Wrapper for classifiers with biometric-specific functionality.
    """
    
    def __init__(self, classifier_type: str = 'svm', **kwargs):
        """
        Initialize classifier.
        
        Args:
            classifier_type: 'svm' or 'rf'
            **kwargs: Additional parameters for the classifier
        """
        self.classifier_type = classifier_type
        
        if classifier_type == 'svm':
            default_params = {'kernel': 'rbf', 'gamma': 'auto', 'C': 1.0}
            default_params.update(kwargs)
            self.classifier = SVC(probability=True, **default_params)
        elif classifier_type == 'rf':
            default_params = {'n_estimators': 100, 'random_state': 42}
            default_params.update(kwargs)
            self.classifier = RandomForestClassifier(**default_params)
        else:
            raise ValueError(f"Unknown classifier type: {classifier_type}")
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Train the classifier.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (0 for impostor, 1 for genuine)
        """
        self.classifier.fit(X, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        return self.classifier.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        return self.classifier.predict_proba(X)
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate accuracy score."""
        return self.classifier.score(X, y)
    
    def cross_validate(self, X: np.ndarray, y: np.ndarray, 
                      cv: int = 5) -> Dict[str, float]:
        """
        Perform cross-validation.
        
        Args:
            X: Feature matrix
            y: Labels
            cv: Number of folds
            
        Returns:
            Dictionary with mean and std of scores
        """
        scores = cross_val_score(self.classifier, X, y, cv=cv, scoring='accuracy')
        return {
            'mean_accuracy': float(np.mean(scores)),
            'std_accuracy': float(np.std(scores)),
            'scores': scores.tolist()
        }


class BiometricMetrics:
    """
    Calculate biometric performance metrics (FAR, FRR, EER).
    """
    
    @staticmethod
    def calculate_far_frr(y_true: np.ndarray, y_scores: np.ndarray, 
                         thresholds: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate False Acceptance Rate (FAR) and False Rejection Rate (FRR).
        
        Args:
            y_true: True labels (0 for impostor, 1 for genuine)
            y_scores: Similarity scores (higher means more similar)
            thresholds: Array of thresholds to evaluate
            
        Returns:
            Tuple of (thresholds, FAR, FRR)
        """
        if thresholds is None:
            thresholds = np.linspace(0, 1, 1000)
        
        far = np.zeros(len(thresholds))
        frr = np.zeros(len(thresholds))
        
        # Separate genuine and impostor scores
        genuine_scores = y_scores[y_true == 1]
        impostor_scores = y_scores[y_true == 0]
        
        for i, threshold in enumerate(thresholds):
            # FAR: Proportion of impostors accepted (impostor score >= threshold)
            if len(impostor_scores) > 0:
                far[i] = np.sum(impostor_scores >= threshold) / len(impostor_scores)
            else:
                far[i] = 0.0
            
            # FRR: Proportion of genuine users rejected (genuine score < threshold)
            if len(genuine_scores) > 0:
                frr[i] = np.sum(genuine_scores < threshold) / len(genuine_scores)
            else:
                frr[i] = 0.0
        
        return thresholds, far, frr
    
    @staticmethod
    def calculate_eer(far: np.ndarray, frr: np.ndarray, 
                     thresholds: np.ndarray) -> Tuple[float, float]:
        """
        Calculate Equal Error Rate (EER).
        
        Args:
            far: False Acceptance Rates
            frr: False Rejection Rates
            thresholds: Threshold values
            
        Returns:
            Tuple of (EER, threshold at EER)
        """
        # Find where FAR = FRR
        # EER is where the difference is minimal
        diff = np.abs(far - frr)
        idx = np.argmin(diff)
        
        eer = (far[idx] + frr[idx]) / 2.0
        eer_threshold = thresholds[idx]
        
        # Alternative: Use interpolation for more precise EER
        try:
            f = interp1d(thresholds, far - frr)
            eer_threshold_interp = brentq(f, thresholds[0], thresholds[-1])
            
            # Recalculate EER at interpolated threshold
            f_far = interp1d(thresholds, far)
            f_frr = interp1d(thresholds, frr)
            eer = (f_far(eer_threshold_interp) + f_frr(eer_threshold_interp)) / 2.0
            eer_threshold = eer_threshold_interp
        except:
            pass  # Use simple method if interpolation fails
        
        return float(eer), float(eer_threshold)
    
    @staticmethod
    def calculate_gar_far_curve(y_true: np.ndarray, y_scores: np.ndarray, 
                               thresholds: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate Genuine Acceptance Rate (GAR) vs FAR curve.
        
        Args:
            y_true: True labels
            y_scores: Similarity scores
            thresholds: Array of thresholds
            
        Returns:
            Tuple of (thresholds, FAR, GAR)
        """
        thresholds, far, frr = BiometricMetrics.calculate_far_frr(y_true, y_scores, thresholds)
        gar = 1.0 - frr  # GAR = 1 - FRR
        
        return thresholds, far, gar
    
    @staticmethod
    def evaluate_system(y_true: np.ndarray, y_scores: np.ndarray, 
                       threshold: float = None) -> Dict[str, float]:
        """
        Comprehensive evaluation of biometric system.
        
        Args:
            y_true: True labels (0 for impostor, 1 for genuine)
            y_scores: Similarity scores
            threshold: Optional decision threshold
            
        Returns:
            Dictionary with all metrics
        """
        # Calculate FAR, FRR, EER
        thresholds, far, frr = BiometricMetrics.calculate_far_frr(y_true, y_scores)
        eer, eer_threshold = BiometricMetrics.calculate_eer(far, frr, thresholds)
        
        # Use EER threshold if not provided
        if threshold is None:
            threshold = eer_threshold
        
        # Get FAR and FRR at operating threshold
        idx = np.argmin(np.abs(thresholds - threshold))
        far_at_threshold = far[idx]
        frr_at_threshold = frr[idx]
        gar_at_threshold = 1.0 - frr_at_threshold
        
        # Convert scores to predictions
        y_pred = (y_scores >= threshold).astype(int)
        
        # Calculate standard metrics
        accuracy = accuracy_score(y_true, y_pred)
        
        # Handle edge cases for precision and recall
        try:
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
        except:
            precision = 0.0
            recall = 0.0
            f1 = 0.0
        
        return {
            'eer': float(eer),
            'eer_threshold': float(eer_threshold),
            'far': float(far_at_threshold),
            'frr': float(frr_at_threshold),
            'gar': float(gar_at_threshold),
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'threshold': float(threshold)
        }
    
    @staticmethod
    def plot_performance_curves(y_true: np.ndarray, y_scores: np.ndarray, 
                              save_path: str = None):
        """
        Plot FAR/FRR curves and ROC-like GAR vs FAR curve.
        
        Args:
            y_true: True labels
            y_scores: Similarity scores
            save_path: Optional path to save figure
        """
        # Calculate curves
        thresholds, far, frr = BiometricMetrics.calculate_far_frr(y_true, y_scores)
        eer, eer_threshold = BiometricMetrics.calculate_eer(far, frr, thresholds)
        gar = 1.0 - frr
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: FAR and FRR vs Threshold
        ax1.plot(thresholds, far, label='FAR (False Acceptance Rate)', linewidth=2)
        ax1.plot(thresholds, frr, label='FRR (False Rejection Rate)', linewidth=2)
        ax1.axvline(eer_threshold, color='r', linestyle='--', 
                   label=f'EER Threshold ({eer_threshold:.3f})')
        ax1.axhline(eer, color='r', linestyle='--', alpha=0.5,
                   label=f'EER ({eer:.3f})')
        ax1.set_xlabel('Threshold')
        ax1.set_ylabel('Error Rate')
        ax1.set_title('FAR and FRR vs Threshold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: GAR vs FAR (ROC-like curve)
        ax2.plot(far, gar, linewidth=2)
        ax2.plot([0, 1], [1, 0], 'r--', alpha=0.5, label='Random Classifier')
        ax2.set_xlabel('FAR (False Acceptance Rate)')
        ax2.set_ylabel('GAR (Genuine Acceptance Rate)')
        ax2.set_title('GAR vs FAR Curve')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 1])
        ax2.set_ylim([0, 1])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig


class ScoreFusion:
    """
    Fuse scores from multiple biometric modalities.
    """
    
    @staticmethod
    def simple_sum(scores: List[float], weights: List[float] = None) -> float:
        """
        Simple weighted sum fusion.
        
        Args:
            scores: List of scores from different modalities
            weights: Optional weights for each modality
            
        Returns:
            Fused score
        """
        if weights is None:
            weights = [1.0] * len(scores)
        
        weights = np.array(weights)
        weights = weights / np.sum(weights)  # Normalize
        
        return float(np.dot(scores, weights))
    
    @staticmethod
    def product_rule(scores: List[float]) -> float:
        """
        Product rule fusion (assumes scores are probabilities).
        
        Args:
            scores: List of probability scores
            
        Returns:
            Fused score
        """
        return float(np.prod(scores))
    
    @staticmethod
    def max_rule(scores: List[float]) -> float:
        """Max rule fusion."""
        return float(np.max(scores))
    
    @staticmethod
    def min_rule(scores: List[float]) -> float:
        """Min rule fusion."""
        return float(np.min(scores))
    
    @staticmethod
    def mean_rule(scores: List[float]) -> float:
        """Mean rule fusion."""
        return float(np.mean(scores))
    
    @staticmethod
    def decision_level_fusion(decisions: List[bool], 
                            strategy: str = 'majority') -> bool:
        """
        Decision-level fusion.
        
        Args:
            decisions: List of boolean decisions from different modalities
            strategy: 'and', 'or', or 'majority'
            
        Returns:
            Fused decision
        """
        if strategy == 'and':
            return all(decisions)
        elif strategy == 'or':
            return any(decisions)
        elif strategy == 'majority':
            return sum(decisions) > len(decisions) / 2
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
