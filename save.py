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
    print(f"✅ Saved {versioned_id} to ChromaDB (stage: {stage})")



