# save.py

import chromadb

# Initialize persistent ChromaDB client once
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection("books_collection")


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
        "versioned_id": versioned_id
    }

    collection.add(
        documents=[content],
        ids=[versioned_id],
        metadatas=[metadata]
    )
    print(f" Saved {versioned_id} to ChromaDB (stage: {stage})")



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
    
    # Optional stage verification
    if stage and metadata.get("stage") != stage:
        print(f"Document {versioned_id} exists but has stage '{metadata.get('stage')}' (expected '{stage}')")
        return {}
    
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