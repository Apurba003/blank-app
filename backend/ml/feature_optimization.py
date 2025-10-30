"""
Feature Optimization Framework

Implements PCA, Genetic Algorithm, and Particle Swarm Optimization
for feature selection and dimensionality reduction.
"""

import numpy as np
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple, Dict, Optional
from deap import base, creator, tools, algorithms
import random


class PCAOptimizer:
    """
    Principal Component Analysis for dimensionality reduction.
    """
    
    def __init__(self, n_components: Optional[int] = None, variance_threshold: float = 0.95):
        """
        Initialize PCA optimizer.
        
        Args:
            n_components: Number of components (None for variance threshold)
            variance_threshold: Cumulative variance to retain
        """
        self.n_components = n_components
        self.variance_threshold = variance_threshold
        self.pca = None
        self.scaler = StandardScaler()
    
    def fit(self, X: np.ndarray) -> 'PCAOptimizer':
        """
        Fit PCA on features.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            
        Returns:
            Self
        """
        # Standardize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Determine number of components
        if self.n_components is None:
            # Use variance threshold
            pca_temp = PCA()
            pca_temp.fit(X_scaled)
            cumsum_variance = np.cumsum(pca_temp.explained_variance_ratio_)
            n_components = np.argmax(cumsum_variance >= self.variance_threshold) + 1
            self.n_components = n_components
        
        # Fit PCA with determined components
        self.pca = PCA(n_components=self.n_components)
        self.pca.fit(X_scaled)
        
        return self
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform features using fitted PCA.
        
        Args:
            X: Feature matrix
            
        Returns:
            Transformed features
        """
        X_scaled = self.scaler.transform(X)
        return self.pca.transform(X_scaled)
    
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit and transform in one step."""
        return self.fit(X).transform(X)
    
    def get_explained_variance(self) -> np.ndarray:
        """Get explained variance ratio for each component."""
        return self.pca.explained_variance_ratio_
    
    def get_n_components(self) -> int:
        """Get number of components."""
        return self.n_components


class GeneticAlgorithmOptimizer:
    """
    Genetic Algorithm for feature selection.
    """
    
    def __init__(self, n_features: int, population_size: int = 50, 
                 n_generations: int = 50, mutation_rate: float = 0.1):
        """
        Initialize GA optimizer.
        
        Args:
            n_features: Total number of features
            population_size: Size of population
            n_generations: Number of generations
            mutation_rate: Probability of mutation
        """
        self.n_features = n_features
        self.population_size = population_size
        self.n_generations = n_generations
        self.mutation_rate = mutation_rate
        self.best_features = None
        self.best_score = 0.0
        
        # Setup DEAP
        if not hasattr(creator, "FitnessMax"):
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMax)
        
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_bool", random.randint, 0, 1)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual,
                            self.toolbox.attr_bool, n=n_features)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=self.mutation_rate)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
    
    def optimize(self, X: np.ndarray, y: np.ndarray, 
                classifier_type: str = 'svm') -> Tuple[List[int], float]:
        """
        Optimize feature selection using GA.
        
        Args:
            X: Feature matrix
            y: Labels
            classifier_type: 'svm' or 'rf'
            
        Returns:
            Tuple of (selected_features, best_score)
        """
        def evaluate_features(individual):
            """Fitness function."""
            # Select features
            selected = [i for i, bit in enumerate(individual) if bit == 1]
            
            if len(selected) == 0:
                return 0.0,
            
            X_selected = X[:, selected]
            
            # Train classifier and get cross-validation score
            if classifier_type == 'svm':
                clf = SVC(kernel='rbf', gamma='auto')
            else:
                clf = RandomForestClassifier(n_estimators=50, random_state=42)
            
            try:
                scores = cross_val_score(clf, X_selected, y, cv=3, scoring='accuracy')
                return scores.mean(),
            except:
                return 0.0,
        
        self.toolbox.register("evaluate", evaluate_features)
        
        # Initialize population
        population = self.toolbox.population(n=self.population_size)
        
        # Statistics
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)
        
        # Run GA
        population, logbook = algorithms.eaSimple(
            population, self.toolbox,
            cxpb=0.7, mutpb=0.2,
            ngen=self.n_generations,
            stats=stats, verbose=False
        )
        
        # Get best individual
        best_ind = tools.selBest(population, 1)[0]
        self.best_features = [i for i, bit in enumerate(best_ind) if bit == 1]
        self.best_score = best_ind.fitness.values[0]
        
        return self.best_features, self.best_score
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform features using selected features."""
        if self.best_features is None:
            raise ValueError("Must call optimize() first")
        return X[:, self.best_features]


class ParticleSwarmOptimizer:
    """
    Particle Swarm Optimization for feature selection.
    """
    
    def __init__(self, n_features: int, n_particles: int = 30, 
                 n_iterations: int = 50):
        """
        Initialize PSO optimizer.
        
        Args:
            n_features: Total number of features
            n_particles: Number of particles in swarm
            n_iterations: Number of iterations
        """
        self.n_features = n_features
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.best_features = None
        self.best_score = 0.0
    
    def optimize(self, X: np.ndarray, y: np.ndarray, 
                classifier_type: str = 'svm') -> Tuple[List[int], float]:
        """
        Optimize feature selection using PSO.
        
        Args:
            X: Feature matrix
            y: Labels
            classifier_type: 'svm' or 'rf'
            
        Returns:
            Tuple of (selected_features, best_score)
        """
        # Initialize particles
        particles = np.random.rand(self.n_particles, self.n_features)
        velocities = np.random.rand(self.n_particles, self.n_features) * 0.1
        
        # Personal best
        pbest = particles.copy()
        pbest_scores = np.zeros(self.n_particles)
        
        # Global best
        gbest = particles[0].copy()
        gbest_score = 0.0
        
        # PSO parameters
        w = 0.7  # inertia
        c1 = 1.5  # cognitive parameter
        c2 = 1.5  # social parameter
        
        def evaluate_particle(particle):
            """Evaluate fitness of a particle."""
            # Convert continuous values to binary (threshold at 0.5)
            binary = (particle > 0.5).astype(int)
            selected = [i for i, bit in enumerate(binary) if bit == 1]
            
            if len(selected) == 0:
                return 0.0
            
            X_selected = X[:, selected]
            
            # Train classifier
            if classifier_type == 'svm':
                clf = SVC(kernel='rbf', gamma='auto')
            else:
                clf = RandomForestClassifier(n_estimators=50, random_state=42)
            
            try:
                scores = cross_val_score(clf, X_selected, y, cv=3, scoring='accuracy')
                return scores.mean()
            except:
                return 0.0
        
        # PSO iterations
        for iteration in range(self.n_iterations):
            for i in range(self.n_particles):
                # Evaluate particle
                score = evaluate_particle(particles[i])
                
                # Update personal best
                if score > pbest_scores[i]:
                    pbest_scores[i] = score
                    pbest[i] = particles[i].copy()
                
                # Update global best
                if score > gbest_score:
                    gbest_score = score
                    gbest = particles[i].copy()
            
            # Update velocities and positions
            r1 = np.random.rand(self.n_particles, self.n_features)
            r2 = np.random.rand(self.n_particles, self.n_features)
            
            velocities = (w * velocities + 
                         c1 * r1 * (pbest - particles) + 
                         c2 * r2 * (gbest - particles))
            
            particles = particles + velocities
            
            # Bound particles to [0, 1]
            particles = np.clip(particles, 0, 1)
        
        # Convert best particle to feature indices
        binary_best = (gbest > 0.5).astype(int)
        self.best_features = [i for i, bit in enumerate(binary_best) if bit == 1]
        self.best_score = gbest_score
        
        return self.best_features, self.best_score
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform features using selected features."""
        if self.best_features is None:
            raise ValueError("Must call optimize() first")
        return X[:, self.best_features]


class FeatureOptimizationPipeline:
    """
    Complete feature optimization pipeline combining multiple techniques.
    """
    
    def __init__(self, optimization_method: str = 'pca'):
        """
        Initialize optimization pipeline.
        
        Args:
            optimization_method: 'pca', 'ga', 'pso', or 'hybrid'
        """
        self.optimization_method = optimization_method
        self.optimizer = None
        self.scaler = StandardScaler()
    
    def fit(self, X: np.ndarray, y: np.ndarray = None) -> 'FeatureOptimizationPipeline':
        """
        Fit the optimization pipeline.
        
        Args:
            X: Feature matrix
            y: Labels (required for GA and PSO)
            
        Returns:
            Self
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        if self.optimization_method == 'pca':
            self.optimizer = PCAOptimizer(variance_threshold=0.95)
            self.optimizer.fit(X_scaled)
            
        elif self.optimization_method == 'ga':
            if y is None:
                raise ValueError("Labels required for GA optimization")
            self.optimizer = GeneticAlgorithmOptimizer(n_features=X.shape[1])
            self.optimizer.optimize(X_scaled, y)
            
        elif self.optimization_method == 'pso':
            if y is None:
                raise ValueError("Labels required for PSO optimization")
            self.optimizer = ParticleSwarmOptimizer(n_features=X.shape[1])
            self.optimizer.optimize(X_scaled, y)
            
        elif self.optimization_method == 'hybrid':
            # Use PCA first, then GA
            if y is None:
                raise ValueError("Labels required for hybrid optimization")
            
            pca = PCAOptimizer(variance_threshold=0.95)
            X_pca = pca.fit_transform(X_scaled)
            
            ga = GeneticAlgorithmOptimizer(n_features=X_pca.shape[1])
            ga.optimize(X_pca, y)
            
            self.optimizer = {'pca': pca, 'ga': ga}
        
        return self
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform features using fitted optimizer.
        
        Args:
            X: Feature matrix
            
        Returns:
            Optimized features
        """
        X_scaled = self.scaler.transform(X)
        
        if self.optimization_method in ['pca', 'ga', 'pso']:
            return self.optimizer.transform(X_scaled)
            
        elif self.optimization_method == 'hybrid':
            X_pca = self.optimizer['pca'].transform(X_scaled)
            return self.optimizer['ga'].transform(X_pca)
    
    def fit_transform(self, X: np.ndarray, y: np.ndarray = None) -> np.ndarray:
        """Fit and transform in one step."""
        return self.fit(X, y).transform(X)
