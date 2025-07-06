import chromadb
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

# Import policy-related functions from rl_search
from rl_search import (
    policy_decision,
    update_policy as update_policy_stage,
    get_policy_insights as get_policy_stats,
    save_policy_weights as save_policy_model
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection("books_collection")

# Placeholder for RL agent (if needed)
class RLSearchAgent:
    """Placeholder RL search agent implementation"""
    def intelligent_search(self, query: str, context: Dict = None, user_feedback: Dict = None) -> List:
        logger.warning("RL search agent not fully implemented - using placeholder")
        return []
    
    def stage_progression_search(self, query: str) -> List:
        return []
    
    def get_search_stats(self) -> Dict:
        return {}
    
    def save_q_table(self):
        logger.info("RL search model save called (placeholder)")

rl_agent = RLSearchAgent()

def get_next_version(base_id: str) -> int:
    """Auto-increment version number for a given base_id."""
    results = collection.get(include=["metadatas"])

    # Filter versions manually
    versions = [
        meta["version"]
        for meta in results["metadatas"]
        if meta.get("versioned_id", "").startswith(base_id)
    ]

    return max(versions, default=0) + 1

def save_chapter_auto_version(data: dict, base_id: str, stage: str) -> bool:
    """Save chapter with auto-incremented version and metadata."""
    try:
        version = get_next_version(base_id)
        versioned_id = f"{base_id}_ver{version}"
        content = data["content"]

        metadata = {
            "book_title": data["book_title"],
            "author": data["author"],
            "chapter_info": data["chapter_info"],
            "chapter_title": data["chapter_title"],
            "source_url": data["source_url"],
            "version": version,
            "stage": stage,
            "versioned_id": versioned_id,
            "reviewer_feedback": data.get("reviewer_feedback", "")
        }

        collection.add(
            documents=[content],
            ids=[versioned_id],
            metadatas=[metadata]
        )
        logger.info(f"Saved {versioned_id} to ChromaDB (stage: {stage})")
        return True
    except Exception as e:
        logger.error(f"Failed to save chapter: {e}")
        return False

def fetch_chapter_by_version(versioned_id: str, stage: str = None) -> dict:
    """Fetch a specific chapter version from ChromaDB."""
    try:
        result = collection.get(ids=[versioned_id], include=["documents", "metadatas"])
        
        if not result["documents"]:
            logger.warning(f"No document found with ID: {versioned_id}")
            return {}
            
        metadata = result["metadatas"][0]
        
        return {
            "content": result["documents"][0],
            "metadata": metadata
        }
    except Exception as e:
        logger.error(f"Error fetching chapter: {e}")
        return {}

def get_latest_version(base_id: str, stage: str) -> int:
    """Get the highest version number for a given base_id and stage"""
    try:
        results = collection.get(include=["metadatas"])
        versions = [
            meta["version"]
            for meta in results["metadatas"]
            if meta.get("versioned_id", "").startswith(base_id)
            and meta.get("stage") == stage
        ]
        return max(versions, default=0)
    except Exception as e:
        logger.error(f"Error getting latest version: {e}")
        return 0

def format_chapter_markdown(chapter_data: dict) -> str:
    """Format chapter data as markdown."""
    try:
        content = chapter_data.get('content', '').strip()
        metadata = chapter_data.get('metadata', {})
        
        book_title = metadata.get('book_title', 'Unknown Book')
        chapter_title = metadata.get('chapter_title', 'Untitled Chapter')
        chapter_info = metadata.get('chapter_info', '')
        author = metadata.get('author', 'Unknown Author')
        version = metadata.get('version', 'N/A')
        stage = metadata.get('stage', 'N/A')
        reviewer_feedback = metadata.get('reviewer_feedback', 'No feedback provided.')
        source_url = metadata.get('source_url', '')

        markdown = f"# 📖 {chapter_title}\n"
        markdown += f"### *{chapter_info} – {book_title}*\n"
        markdown += f"**Author:** {author}  \n"
        markdown += f"**Version:** {version} | **Stage:** {stage}  \n"
        if source_url:
            markdown += f"[🔗 Source]({source_url})\n"
        markdown += "\n---\n\n"
        markdown += "## 📝 Content:\n\n"
        markdown += "```\n" + content + "\n```\n\n"
        markdown += "---\n\n"
        markdown += "## 🧾 Reviewer Feedback:\n"
        markdown += "> " + reviewer_feedback.replace('\n', '\n> ') + "\n"

        return markdown
    except Exception as e:
        logger.error(f"Error formatting markdown: {e}")
        return "Error formatting content"

# Search-related functions (using placeholder RL agent)
def intelligent_search(query: str, context: dict = None, user_feedback: dict = None) -> list:
    """Intelligent content search with RL integration."""
    try:
        return rl_agent.intelligent_search(query, context, user_feedback)
    except Exception as e:
        logger.error(f"Intelligent search failed: {e}")
        return []

def search_by_stage_progression(query: str) -> list:
    """Search following the editing workflow progression."""
    try:
        return rl_agent.stage_progression_search(query)
    except Exception as e:
        logger.error(f"Stage progression search failed: {e}")
        return []

def search_latest_content(base_id: str = "chapter1") -> list:
    """Get the latest version of content."""
    try:
        context = {"base_id": base_id}
        return rl_agent.get_latest_version_search(base_id)
    except Exception as e:
        logger.error(f"Latest content search failed: {e}")
        return []

def provide_search_feedback(clicked_result: bool = False, satisfaction_score: int = 3) -> dict:
    """Provide feedback to improve search results."""
    try:
        return {
            "clicked_result": clicked_result,
            "satisfaction_score": satisfaction_score
        }
    except Exception as e:
        logger.error(f"Error providing search feedback: {e}")
        return {}

def get_search_analytics() -> dict:
    """Get RL search performance analytics."""
    try:
        return rl_agent.get_search_stats()
    except Exception as e:
        logger.error(f"Error getting search analytics: {e}")
        return {}

def save_rl_model() -> bool:
    """Save the trained RL model."""
    try:
        rl_agent.save_q_table()
        logger.info("RL search model saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving RL model: {e}")
        return False

# Policy-related functions (now properly integrated)
def select_policy_stage(context: dict = None) -> str:
    """Choose a stage using policy-based agent."""
    try:
        return policy_decision(context)
    except Exception as e:
        logger.error(f"Policy stage selection failed: {e}")
        return "raw"  # Default fallback

def update_policy(action: str, reward: int = 3) -> bool:
    """Update policy based on user feedback."""
    try:
        update_policy_stage(action, reward)
        return True
    except Exception as e:
        logger.error(f"Policy update failed: {e}")
        return False

def get_policy_insights() -> dict:
    """Return current policy weights and probabilities."""
    try:
        return get_policy_stats()
    except Exception as e:
        logger.error(f"Error getting policy insights: {e}")
        return {
            "error": str(e),
            "default_preferences": {"raw": 1.0, "rewritten": 1.0, "edited": 1.0}
        }

def save_policy() -> bool:
    """Persist the policy agent's learned weights."""
    try:
        save_policy_model()
        return True
    except Exception as e:
        logger.error(f"Error saving policy: {e}")
        return False