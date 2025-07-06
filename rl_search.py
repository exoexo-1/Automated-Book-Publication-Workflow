from policy_search_agent import PolicySearchAgent
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global policy agent instance
policy_agent = PolicySearchAgent()

def policy_decision(context=None):
    """Make policy decision with optional context"""
    try:
        if context:
            logger.info(f"Making policy decision with context: {context}")
        return policy_agent.select_action(context)
    except Exception as e:
        logger.error(f"Policy decision failed: {e}")
        return "raw"  # Default fallback

def update_policy(action, reward):
    """Update policy based on action and reward"""
    try:
        policy_agent.update_policy(action, float(reward))
        return True
    except Exception as e:
        logger.error(f"Policy update failed: {e}")
        return False

def save_policy_weights():
    """Persist policy weights"""
    try:
        policy_agent.save_policy()
        return True
    except Exception as e:
        logger.error(f"Failed to save policy weights: {e}")
        return False

def get_policy_insights():
    """Get current policy state"""
    try:
        return policy_agent.get_policy()
    except Exception as e:
        logger.error(f"Failed to get policy insights: {e}")
        return {
            "preferences": {a: 1.0 for a in policy_agent.actions},
            "probabilities": {a: 1.0/len(policy_agent.actions) for a in policy_agent.actions},
            "error": str(e)
        }