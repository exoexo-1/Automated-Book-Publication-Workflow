
# save.py 

import chromadb
from rl_search import create_rl_search_agent

chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection("books_collection")

rl_agent = create_rl_search_agent(chroma_client)

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

def save_chapter_auto_version(data: dict, base_id: str, stage:str):
    """Save chapter with auto-incremented version and metadata."""
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
    print("\n\n",f" Saved {versioned_id} to ChromaDB (stage: {stage})","\n\n")



def fetch_chapter_by_version(versioned_id: str, stage: str = None) -> dict:
    """Fetch a specific chapter version from ChromaDB using versioned_id (e.g., chapter1_ver2).
    
    Args:
        versioned_id: The full versioned ID (e.g., "chapter1_ver1")
        stage: Optional filter for stage (raw/rewritten/edited)
    """
    result = collection.get(ids=[versioned_id], include=["documents", "metadatas"])
    
    if not result["documents"]:
        print(f"No document found with ID: {versioned_id}")
        return {}
        
    metadata = result["metadatas"][0]
    
    return {
        "content": result["documents"][0],
        "metadata": metadata
    }


def get_latest_version(base_id: str, stage: str) -> int:
    """Get the highest version number for a given base_id and stage"""
    results = collection.get(include=["metadatas"])
    versions = [
        meta["version"]
        for meta in results["metadatas"]
        if meta.get("versioned_id", "").startswith(base_id)
        and meta.get("stage") == stage
    ]
    return max(versions, default=0)


def format_chapter_markdown(chapter_data):
    content = chapter_data.get('content', '').strip()
    metadata = chapter_data.get('metadata', {})
    
    # Metadata fields
    book_title = metadata.get('book_title', 'Unknown Book')
    chapter_title = metadata.get('chapter_title', 'Untitled Chapter')
    chapter_info = metadata.get('chapter_info', '')
    author = metadata.get('author', 'Unknown Author')
    version = metadata.get('version', 'N/A')
    stage = metadata.get('stage', 'N/A')
    reviewer_feedback = metadata.get('reviewer_feedback', 'No feedback provided.')
    source_url = metadata.get('source_url', '')

    # Markdown formatting
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



def intelligent_search(query: str, context: dict = None, user_feedback: dict = None) -> list:
    """
    Use RL agent for intelligent content search
    
    Args:
        query: Search query string
        context: Search context (preferred_stage, base_id, etc.)
        user_feedback: User feedback for learning (clicked_result, satisfaction_score)
    
    Returns:
        List of search results with content and metadata
    """
    return rl_agent.intelligent_search(query, context, user_feedback)

def search_by_stage_progression(query: str) -> list:
    """Search following the editing workflow progression"""
    return rl_agent.stage_progression_search(query)

def search_latest_content(base_id: str = "chapter1") -> list:
    """Get the latest version of content using RL search"""
    context = {"base_id": base_id}
    return rl_agent.get_latest_version_search(base_id)

def provide_search_feedback(clicked_result: bool = False, satisfaction_score: int = 3):
    """
    Provide feedback to improve search results
    
    Args:
        clicked_result: Whether user clicked on a search result
        satisfaction_score: User satisfaction (1-5 scale)
    """
    return {
        "clicked_result": clicked_result,
        "satisfaction_score": satisfaction_score
    }

def get_search_analytics() -> dict:
    """Get RL search performance analytics"""
    return rl_agent.get_search_stats()

def save_rl_model():
    """Save the trained RL model"""
    rl_agent.save_q_table()
    print("RL search model saved successfully")