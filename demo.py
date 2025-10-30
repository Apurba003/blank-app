#!/usr/bin/env python3
"""
Demo script for the Multi-Factor Authentication System

This script demonstrates the core functionality of the biometric authentication system.
"""

import sys
sys.path.insert(0, 'backend')

import numpy as np
from biometrics.keystroke_dynamics import KeystrokeDynamicsAuth
from ml.feature_optimization import PCAOptimizer
from ml.classifiers import BiometricMetrics, ScoreFusion

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def demo_keystroke_dynamics():
    """Demonstrate keystroke dynamics authentication."""
    print_header("Keystroke Dynamics Authentication Demo")
    
    # Create sample keystroke data for a genuine user
    genuine_session = [
        {'key': 'p', 'press_time': 0.00, 'release_time': 0.10, 'pressure': 0.5},
        {'key': 'a', 'press_time': 0.15, 'release_time': 0.25, 'pressure': 0.6},
        {'key': 's', 'press_time': 0.30, 'release_time': 0.40, 'pressure': 0.55},
        {'key': 's', 'press_time': 0.45, 'release_time': 0.55, 'pressure': 0.52},
        {'key': 'w', 'press_time': 0.60, 'release_time': 0.70, 'pressure': 0.58},
        {'key': 'o', 'press_time': 0.75, 'release_time': 0.85, 'pressure': 0.53},
        {'key': 'r', 'press_time': 0.90, 'release_time': 1.00, 'pressure': 0.57},
        {'key': 'd', 'press_time': 1.05, 'release_time': 1.15, 'pressure': 0.54},
    ]
    
    # Create impostor session (different timing patterns)
    impostor_session = [
        {'key': 'p', 'press_time': 0.00, 'release_time': 0.15, 'pressure': 0.7},
        {'key': 'a', 'press_time': 0.20, 'release_time': 0.35, 'pressure': 0.8},
        {'key': 's', 'press_time': 0.40, 'release_time': 0.50, 'pressure': 0.65},
        {'key': 's', 'press_time': 0.60, 'release_time': 0.75, 'pressure': 0.72},
        {'key': 'w', 'press_time': 0.80, 'release_time': 0.95, 'pressure': 0.68},
        {'key': 'o', 'press_time': 1.00, 'release_time': 1.15, 'pressure': 0.73},
        {'key': 'r', 'press_time': 1.20, 'release_time': 1.30, 'pressure': 0.67},
        {'key': 'd', 'press_time': 1.35, 'release_time': 1.50, 'pressure': 0.74},
    ]
    
    # Enroll user with multiple sessions
    sessions = [genuine_session.copy() for _ in range(5)]
    
    auth = KeystrokeDynamicsAuth()
    print("📝 Enrolling user 'alice'...")
    template = auth.enroll_user('alice', sessions)
    print(f"✓ User enrolled successfully")
    print(f"  - Training sessions: {len(sessions)}")
    print(f"  - Feature dimensions: {len(template.template['mean'])}")
    
    # Test genuine authentication
    print("\n🔑 Testing genuine user authentication...")
    is_auth, score, details = auth.authenticate('alice', genuine_session)
    print(f"  Result: {'✓ AUTHENTICATED' if is_auth else '✗ REJECTED'}")
    print(f"  Similarity score: {score:.4f}")
    
    # Test impostor authentication
    print("\n🚫 Testing impostor authentication...")
    is_auth, score, details = auth.authenticate('alice', impostor_session)
    print(f"  Result: {'✓ AUTHENTICATED' if is_auth else '✗ REJECTED'}")
    print(f"  Similarity score: {score:.4f}")

def demo_feature_optimization():
    """Demonstrate feature optimization with PCA."""
    print_header("Feature Optimization with PCA Demo")
    
    # Generate sample feature data
    np.random.seed(42)
    n_samples = 100
    n_features = 50
    
    print(f"📊 Generating sample data:")
    print(f"  - Samples: {n_samples}")
    print(f"  - Original features: {n_features}")
    
    X = np.random.randn(n_samples, n_features)
    
    # Apply PCA
    print("\n🔬 Applying PCA for dimensionality reduction...")
    pca = PCAOptimizer(variance_threshold=0.95)
    X_reduced = pca.fit_transform(X)
    
    print(f"✓ PCA completed")
    print(f"  - Reduced features: {X_reduced.shape[1]}")
    print(f"  - Variance retained: {pca.get_explained_variance()[:5].sum():.2%}")
    print(f"  - Dimensionality reduction: {(1 - X_reduced.shape[1]/n_features)*100:.1f}%")

def demo_biometric_metrics():
    """Demonstrate biometric performance metrics."""
    print_header("Biometric Performance Metrics Demo")
    
    # Simulate authentication scores
    np.random.seed(42)
    
    # Genuine user scores (higher, around 0.7-0.9)
    genuine_scores = np.random.normal(0.8, 0.1, 100)
    genuine_scores = np.clip(genuine_scores, 0, 1)
    
    # Impostor scores (lower, around 0.2-0.5)
    impostor_scores = np.random.normal(0.35, 0.15, 100)
    impostor_scores = np.clip(impostor_scores, 0, 1)
    
    # Combine scores and labels
    y_scores = np.concatenate([genuine_scores, impostor_scores])
    y_true = np.concatenate([np.ones(100), np.zeros(100)])
    
    print("📊 Calculating biometric metrics...")
    print(f"  - Genuine samples: {len(genuine_scores)}")
    print(f"  - Impostor samples: {len(impostor_scores)}")
    
    # Calculate metrics
    metrics = BiometricMetrics.evaluate_system(y_true, y_scores)
    
    print(f"\n📈 Performance Metrics:")
    print(f"  - Equal Error Rate (EER): {metrics['eer']:.4f} ({metrics['eer']*100:.2f}%)")
    print(f"  - False Acceptance Rate (FAR): {metrics['far']:.4f} ({metrics['far']*100:.2f}%)")
    print(f"  - False Rejection Rate (FRR): {metrics['frr']:.4f} ({metrics['frr']*100:.2f}%)")
    print(f"  - Genuine Acceptance Rate (GAR): {metrics['gar']:.4f} ({metrics['gar']*100:.2f}%)")
    print(f"  - Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"  - Operating threshold: {metrics['threshold']:.4f}")

def demo_score_fusion():
    """Demonstrate multi-modal score fusion."""
    print_header("Multi-Modal Score Fusion Demo")
    
    # Simulate scores from different modalities
    keystroke_score = 0.75
    face_score = 0.85
    
    print("🔐 Input scores:")
    print(f"  - Keystroke dynamics: {keystroke_score:.4f}")
    print(f"  - Face recognition: {face_score:.4f}")
    
    print("\n🔀 Fusion methods:")
    
    # Weighted sum (face weighted more)
    fused = ScoreFusion.simple_sum([keystroke_score, face_score], [0.4, 0.6])
    print(f"  - Weighted sum (40% keystroke, 60% face): {fused:.4f}")
    
    # Mean
    fused = ScoreFusion.mean_rule([keystroke_score, face_score])
    print(f"  - Mean: {fused:.4f}")
    
    # Product
    fused = ScoreFusion.product_rule([keystroke_score, face_score])
    print(f"  - Product: {fused:.4f}")
    
    # Max
    fused = ScoreFusion.max_rule([keystroke_score, face_score])
    print(f"  - Max: {fused:.4f}")
    
    # Min
    fused = ScoreFusion.min_rule([keystroke_score, face_score])
    print(f"  - Min: {fused:.4f}")

def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("  Multi-Factor Authentication System - Demo")
    print("="*60)
    
    try:
        demo_keystroke_dynamics()
        demo_feature_optimization()
        demo_biometric_metrics()
        demo_score_fusion()
        
        print("\n" + "="*60)
        print("  ✅ All demos completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
