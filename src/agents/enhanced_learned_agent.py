import numpy as np
import torch
from pathlib import Path
from typing import Dict, Optional, Tuple

from ..data.conditional_data_generator import ConditionalDataGenerator
from ..models.advanced_neural_tom import AdvancedNeuralToM, AdvancedToMTrainer
from ..models.mental_states import MentalState
from ..models.negotiation_state import NegotiationState


class EnhancedLearnedAgent:
    """Learned ToM agent backed by a neural ToM model.

    This class matches the common agent interface expected by experiment runners:
    - choose_action(state) -> (share_agent0, share_agent1)
    - update_beliefs(...)
    - get_mental_state() -> object with .warmth/.competence
    """

    def __init__(
        self,
        lambda_social: float = 0.5,
        agent_id: int = 0,
        agent_type: str = "learned_tom",
        model_path: str = "best_neural_tom.pth",
        model: Optional[AdvancedNeuralToM] = None,
        train_if_missing: bool = False,
        device: Optional[str] = None,
    ):
        self.lambda_social = float(lambda_social)
        self.agent_id = int(agent_id)
        self.agent_type = agent_type

        self.model_path = str(model_path) if model_path is not None else "best_neural_tom.pth"
        self.train_if_missing = bool(train_if_missing)
        self.device = torch.device(device) if device is not None else torch.device("cpu")

        self.model = model if model is not None else AdvancedNeuralToM()
        self.model.to(self.device)
        self._maybe_load_or_train_model()

        self.mental_state = MentalState(warmth=0.5, competence=0.5)
        self._uncertainty = 0.3

        self.decision_history = []

    def _maybe_load_or_train_model(self) -> None:
        path = Path(self.model_path)
        if path.exists():
            state_dict = torch.load(str(path), map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.eval()
            return

        if self.train_if_missing:
            self.model = self._train_advanced_model()
            self.model.to(self.device)
            self.model.eval()
            return

        # Fast, non-blocking fallback: keep randomly initialized weights.
        # This makes the agent runnable even when the pretrained checkpoint
        # hasn't been downloaded.
        self.model.eval()
    
    def _train_advanced_model(self) -> AdvancedNeuralToM:
        """
        Train the advanced NeuralToM model on conditional data.
        """
        print("🚀 Training Advanced NeuralToM with conditional reasoning...")
        generator = ConditionalDataGenerator()
        X, y = generator.generate_training_data(n_samples=8000)
        
        model = AdvancedNeuralToM().to(self.device)
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

            # Multiple forward passes for uncertainty estimation (MC dropout)
            predictions = []
            for _ in range(10):
                input_tensor = torch.tensor(
                    [[offer_norm, lambda_norm]],
                    dtype=torch.float32,
                    device=self.device,
                )
                pred = self.model(input_tensor)
                predictions.append(pred[0].detach().cpu().tolist())

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
        """Compatibility shim: return this agent's integer share."""
        action = self.choose_action(negotiation_state)
        return int(action[self.agent_id])

    def choose_action(self, negotiation_state: NegotiationState) -> Tuple[int, int]:
        """Choose the split that maximizes learned expected utility."""
        total = negotiation_state.total_resources
        best_offer_for_self = 1
        best_utility = -float('inf')
        best_evaluation = None

        for offer_for_self in range(1, total):
            evaluation = self.evaluate_offer(offer_for_self, negotiation_state)
            utility = evaluation.get('expected_utility', -float('inf'))
            if utility > best_utility:
                best_utility = utility
                best_offer_for_self = offer_for_self
                best_evaluation = evaluation

        if best_evaluation is not None:
            self.mental_state.warmth = float(best_evaluation['predicted_warmth'])
            self.mental_state.competence = float(best_evaluation['predicted_competence'])
            self._uncertainty = float(
                (best_evaluation['warmth_uncertainty'] + best_evaluation['competence_uncertainty']) / 2
            )

        action = (
            (best_offer_for_self, total - best_offer_for_self)
            if self.agent_id == 0
            else (total - best_offer_for_self, best_offer_for_self)
        )

        self.decision_history.append(
            {
                'offer_for_self': best_offer_for_self,
                'action': action,
                'mental_state': {
                    'warmth': float(self.mental_state.warmth),
                    'competence': float(self.mental_state.competence),
                    'uncertainty': float(self._uncertainty),
                },
                'evaluation': best_evaluation,
            }
        )

        return action

    def update_beliefs(
        self,
        state: NegotiationState,
        action: Tuple[int, int],
        response: bool,
        opponent_action: Tuple[int, int] = None,
        observer_feedback=None,
        feedback_reliability: Optional[float] = None,
    ):
        """Update the agent's internal mental-state estimate.

        The learned agent doesn't maintain a Bayesian belief state; this is a lightweight
        adapter so it plays nicely with the experiment runners.
        """
        if observer_feedback is None:
            return

        w_delta, c_delta = observer_feedback
        rel = float(feedback_reliability) if feedback_reliability is not None else 1.0
        rel = float(np.clip(rel, 0.0, 1.0))
        gain = 0.25 * (0.4 + 0.6 * rel)

        self.mental_state.warmth = float(np.clip(self.mental_state.warmth + gain * w_delta, 0.0, 1.0))
        self.mental_state.competence = float(np.clip(self.mental_state.competence + gain * c_delta, 0.0, 1.0))

    def get_mental_state(self):
        return self.mental_state
    
    def __str__(self):
        return f"{self.agent_type}(λ={self.lambda_social}, id={self.agent_id})"


# Backwards-compatible alias (older name)
EnhancedLearnedMToM = EnhancedLearnedAgent