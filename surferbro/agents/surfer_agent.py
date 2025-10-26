"""SurferBro agent wrapper for trained models."""

from typing import Optional
import numpy as np
from stable_baselines3 import PPO, SAC, TD3


class SurferAgent:
    """Wrapper for trained SurferBro agents."""

    def __init__(self, model_path: str, algorithm: str = 'PPO'):
        """
        Initialize agent.

        Args:
            model_path: Path to trained model
            algorithm: Algorithm type ('PPO', 'SAC', 'TD3')
        """
        self.algorithm = algorithm

        # Load model
        algorithm_class = {
            'PPO': PPO,
            'SAC': SAC,
            'TD3': TD3
        }[algorithm]

        self.model = algorithm_class.load(model_path)

    def predict(
        self,
        observation: np.ndarray,
        deterministic: bool = True
    ) -> np.ndarray:
        """
        Predict action from observation.

        Args:
            observation: Environment observation
            deterministic: Use deterministic policy

        Returns:
            Action array
        """
        action, _ = self.model.predict(observation, deterministic=deterministic)
        return action

    def get_skill_level(self) -> str:
        """
        Estimate agent's skill level based on model.
        This is a placeholder - could be enhanced with actual performance metrics.

        Returns:
            Skill level string
        """
        # Could analyze model's performance or training metrics
        # For now, just a simple placeholder
        return "Pro Surfer"
