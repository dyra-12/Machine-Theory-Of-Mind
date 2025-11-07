import numpy as np
import torch
from typing import Tuple

class ConditionalDataGenerator:
    """
    Generates training data where human responses strongly depend on social preferences (lambda).
    This forces the neural network to learn conditional reasoning.
    """
    
    def __init__(self, total_resources: int = 10):
        self.total_resources = total_resources
        
    def generate_conditional_response(self, offer_self: int, lambda_val: float) -> Tuple[float, float]:
        """
        Generate human responses that strongly depend on lambda values.
        Social-focused agents care more about warmth, task-focused care more about competence.
        """
        ratio = offer_self / self.total_resources
        
        # Base perceptions vary strongly with lambda
        if lambda_val > 1.2:  # STRONGLY SOCIAL-FOCUSED
            if ratio <= 0.3:
                warmth = np.random.normal(0.95, 0.03)  # Very high warmth
                competence = np.random.normal(0.15, 0.05)  # Very low competence
            elif ratio <= 0.5:
                warmth = np.random.normal(0.80, 0.06)
                competence = np.random.normal(0.40, 0.08)
            elif ratio <= 0.7:
                warmth = np.random.normal(0.50, 0.08)
                competence = np.random.normal(0.70, 0.06)
            else:
                warmth = np.random.normal(0.20, 0.05)
                competence = np.random.normal(0.85, 0.04)
                
        elif lambda_val > 0.6:  # BALANCED
            if ratio <= 0.3:
                warmth = np.random.normal(0.85, 0.05)
                competence = np.random.normal(0.25, 0.07)
            elif ratio <= 0.5:
                warmth = np.random.normal(0.65, 0.07)
                competence = np.random.normal(0.65, 0.07)
            elif ratio <= 0.7:
                warmth = np.random.normal(0.45, 0.07)
                competence = np.random.normal(0.75, 0.05)
            else:
                warmth = np.random.normal(0.25, 0.06)
                competence = np.random.normal(0.80, 0.05)
                
        else:  # TASK-FOCUSED
            if ratio <= 0.3:
                warmth = np.random.normal(0.70, 0.07)
                competence = np.random.normal(0.35, 0.08)
            elif ratio <= 0.5:
                warmth = np.random.normal(0.50, 0.08)
                competence = np.random.normal(0.60, 0.08)
            elif ratio <= 0.7:
                warmth = np.random.normal(0.30, 0.07)
                competence = np.random.normal(0.80, 0.06)
            else:
                warmth = np.random.normal(0.15, 0.04)
                competence = np.random.normal(0.90, 0.03)
        
        # Add some noise based on individual differences
        warmth += np.random.normal(0, 0.02)
        competence += np.random.normal(0, 0.02)
        
        # Clip to valid range
        warmth = np.clip(warmth, 0.01, 0.99)
        competence = np.clip(competence, 0.01, 0.99)
        
        return warmth, competence
    
    def generate_training_data(self, n_samples: int = 8000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate training data with strong lambda conditioning.
        """
        X = []
        y = []
        
        for _ in range(n_samples):
            offer = np.random.randint(1, self.total_resources)
            lambda_val = np.random.uniform(0.1, 2.0)
            
            warmth, competence = self.generate_conditional_response(offer, lambda_val)
            
            # Input: [offer_ratio, lambda]
            X.append([offer / self.total_resources, lambda_val])
            
            # Output: [warmth, competence]
            y.append([warmth, competence])
        
        return np.array(X), np.array(y)