import numpy as np
import torch
from typing import Dict
from ..models.advanced_neural_tom import AdvancedNeuralToM, AdvancedToMTrainer
from ..data.conditional_data_generator import ConditionalDataGenerator
from ..models.negotiation_state import NegotiationState

class EnhancedLearnedMToM:
    """
    Enhanced Learned MToM agent with advanced neural architecture.
    Uses conditional reasoning based on social preferences.
    """
    
    def __init__(self, lambda_social: float = 0.5, agent_type: str = "enhanced_learned",
                 model: AdvancedNeuralToM = None):
        self.lambda_social = lambda_social
        self.agent_type = agent_type
        
        # Use provided model or create and train a new one
        if model is None:
            self.model = self._train_advanced_model()
        else:
            self.model = model
            
        # Mental state tracking
        self.mental_state = {
            'warmth': 0.5,
            'competence': 0.5,
            'uncertainty': 0.3
        }
        
        self.decision_history = []
    
    def _train_advanced_model(self) -> AdvancedNeuralToM:
        """
        Train the advanced NeuralToM model on conditional data.
        """
        print("🚀 Training Advanced NeuralToM with conditional reasoning...")
        generator = ConditionalDataGenerator()
        X, y = generator.generate_training_data(n_samples=8000)
        
        model = AdvancedNeuralToM()
        trainer = AdvancedToMTrainer(model)
        
        results = trainer.train(X, y, epochs=200, batch_size=64)
        print(f"✅ Advanced training completed. Best loss: {results['best_val_loss']:.5f}")
        
        return model
    
    def evaluate_offer(self, offer_self: int, negotiation_state: NegotiationState) -> Dict:
        """
        Enhanced evaluation with uncertainty estimation.
        """
        # Task reward
        task_reward = (offer_self / negotiation_state.total_resources) ** 0.8
        
        # Neural network prediction
        self.model.eval()
        with torch.no_grad():
            offer_norm = offer_self / negotiation_state.total_resources
            lambda_norm = self.lambda_social / 2.0  # Normalize
            
            # Multiple forward passes for uncertainty estimation
            predictions = []
            for _ in range(10):  # Monte Carlo dropout for uncertainty
                input_tensor = torch.tensor([[offer_norm, lambda_norm]], dtype=torch.float32)
                pred = self.model(input_tensor)
                predictions.append(pred[0].tolist())
            
            predictions = np.array(predictions)
            warmth_mean = float(np.mean(predictions[:, 0]))
            competence_mean = float(np.mean(predictions[:, 1]))
            warmth_uncertainty = float(np.std(predictions[:, 0]))
            competence_uncertainty = float(np.std(predictions[:, 1]))
        
        # Social reward (emphasize warmth more for social agents)
        if self.lambda_social > 1.0:
            social_weight = 0.8  # Heavy warmth weighting
        elif self.lambda_social > 0.5:
            social_weight = 0.6  # Balanced weighting
        else:
            social_weight = 0.4  # Light warmth weighting
            
        social_reward = (social_weight * warmth_mean + (1 - social_weight) * competence_mean)
        
        # Total utility with uncertainty penalty
        uncertainty_penalty = 0.1 * (warmth_uncertainty + competence_uncertainty)
        total_utility = task_reward + self.lambda_social * social_reward - uncertainty_penalty
        
        return {
            'expected_utility': total_utility,
            'task_reward': task_reward,
            'predicted_warmth': warmth_mean,
            'predicted_competence': competence_mean,
            'warmth_uncertainty': warmth_uncertainty,
            'competence_uncertainty': competence_uncertainty,
            'social_reward': social_reward,
            'uncertainty_penalty': uncertainty_penalty
        }
    
    def make_offer(self, negotiation_state: NegotiationState) -> int:
        """
        Choose offer with exploration based on uncertainty.
        """
        best_offer = 1
        best_utility = -float('inf')
        best_evaluation = None
        
        evaluations = []
        
        # Evaluate all possible offers
        for offer in range(1, negotiation_state.total_resources):
            evaluation = self.evaluate_offer(offer, negotiation_state)
            evaluations.append((offer, evaluation))
            
            if evaluation['expected_utility'] > best_utility:
                best_utility = evaluation['expected_utility']
                best_offer = offer
                best_evaluation = evaluation
        
        # Update mental state
        self.mental_state['warmth'] = best_evaluation['predicted_warmth']
        self.mental_state['competence'] = best_evaluation['predicted_competence']
        self.mental_state['uncertainty'] = (best_evaluation['warmth_uncertainty'] + 
                                          best_evaluation['competence_uncertainty']) / 2
        
        # Record decision
        self.decision_history.append({
            'offer': best_offer,
            'mental_state': self.mental_state.copy(),
            'evaluation': best_evaluation
        })
        
        return best_offer
    
    def get_mental_state(self) -> Dict:
        return self.mental_state.copy()
    
    def __str__(self):
        return f"EnhancedLearnedMToM(λ={self.lambda_social})"