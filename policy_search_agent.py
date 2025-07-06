import numpy as np
import json
import logging
from pathlib import Path

class PolicySearchAgent:
    def __init__(self, actions=None, learning_rate=0.01, temp=1.0, policy_path="policy_weights.json"):
        self.actions = actions or ["raw", "rewritten", "edited"]
        self.learning_rate = learning_rate
        self.temp = temp  # Temperature for softmax
        self.policy_path = policy_path
        self.preferences = {action: 1.0 for action in self.actions}  # Initialize with equal preferences
        self.load_policy()
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def softmax(self, prefs):
        """Compute softmax probabilities with temperature"""
        scaled_prefs = np.array(list(prefs.values())) / self.temp
        e_prefs = np.exp(scaled_prefs - np.max(scaled_prefs))  # Numerical stability
        return e_prefs / np.sum(e_prefs)

    def validate_action(self, action):
        """Validate that action exists in action space"""
        if action not in self.actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {self.actions}")

    def select_action(self, context=None):
        """Select an action based on current policy"""
        try:
            probs = self.softmax(self.preferences)
            selected = np.random.choice(self.actions, p=probs)
            self.logger.info(f"Selected action: {selected} with probabilities: {dict(zip(self.actions, probs))}")
            return selected
        except Exception as e:
            self.logger.error(f"Action selection failed: {e}")
            return self.actions[0]  # Fallback to first action

    def update_policy(self, action_taken, reward):
        """Update policy weights based on reward"""
        try:
            self.validate_action(action_taken)
            reward = float(reward)
            
            # Clip reward to reasonable range
            reward = np.clip(reward, -1, 1)
            
            # Update preferences
            baseline = np.mean(list(self.preferences.values()))
            for action in self.actions:
                if action == action_taken:
                    self.preferences[action] += self.learning_rate * (reward - baseline)
                else:
                    self.preferences[action] -= self.learning_rate * (reward - baseline) * 0.1
            
            self.logger.info(f"Updated preferences: {self.preferences}")
        except Exception as e:
            self.logger.error(f"Policy update failed: {e}")

    def get_policy(self):
        """Return current policy state"""
        return {
            "preferences": self.preferences.copy(),
            "probabilities": dict(zip(self.actions, self.softmax(self.preferences))),
            "temperature": self.temp,
            "learning_rate": self.learning_rate
        }

    def save_policy(self, path=None):
        """Save policy weights to file"""
        path = path or self.policy_path
        try:
            with open(path, "w") as f:
                json.dump(self.preferences, f)
            self.logger.info(f"Policy saved to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save policy: {e}")

    def load_policy(self, path=None):
        """Load policy weights from file"""
        path = path or self.policy_path
        try:
            if Path(path).exists():
                with open(path, "r") as f:
                    loaded_prefs = json.load(f)
                    # Only load preferences for existing actions
                    self.preferences = {k: loaded_prefs.get(k, 1.0) for k in self.actions}
                self.logger.info(f"Policy loaded from {path}")
        except Exception as e:
            self.logger.error(f"Failed to load policy: {e}")
            # Maintain current preferences if load fails