from save import save_chapter_auto_version, get_latest_version, fetch_chapter_by_version
import google.generativeai as genai
import os
from dotenv import load_dotenv
import textwrap
import time

# Load environment variables
load_dotenv(override=True)
google_api_key = os.getenv('GOOGLE_API_KEY')

if not google_api_key:
    raise ValueError("Google API Key not set in environment variables")

# Configure Gemini
genai.configure(api_key=google_api_key)

SYSTEM_PROMPT = textwrap.dedent("""
    You are a professional book editor and rewriter specializing in literary fiction. 
    Your task is to rewrite book chapters "spinning" while:
    1. Preserving the original meaning and key plot points
    2. Enhancing clarity and readability
    3. Improving narrative flow
    4. Maintaining consistent tone (literary, slightly formal)
    5. Keeping all factual information intact
    
    Rules:
    - Never add new plot elements or characters
    - Preserve all dialogue but improve its naturalness
    - Target word count should be ±10% of original
""")

USER_PROMPT_TEMPLATE = textwrap.dedent("""
    Rewrite this chapter while following all guidelines above:
    
    --- CHAPTER METADATA ---
    Title: {chapter_title}
    From Book: {book_title}
    Author: {author}
    Original Word Count: {word_count}
    
    --- CONTENT TO REWRITE ---
    {content}
    
    --- SPECIAL INSTRUCTIONS ---
    {special_instructions}
""")

def count_words(text: str) -> int:
    return len(text.split())

def rewrite_chapter(versioned_id: str, special_instructions: str = "None") -> dict:
    """
    Fetch a raw chapter from ChromaDB and rewrite it using Gemini
    Returns the rewritten content with metadata
    """
    # Fetch original chapter with stage parameter
    original_data = fetch_chapter_by_version(versioned_id, stage="raw")
    if not original_data:
        raise ValueError(f"No chapter found with ID: {versioned_id}")
    
    content = original_data["content"]
    metadata = original_data["metadata"]
    
    # Prepare prompt
    user_prompt = USER_PROMPT_TEMPLATE.format(
        chapter_title=metadata["chapter_title"],
        book_title=metadata["book_title"],
        author=metadata["author"],
        word_count=count_words(content),
        content=content,
        special_instructions=special_instructions
    )
    
    # Generate rewrite with retry logic
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',  
        system_instruction=SYSTEM_PROMPT
    )
    
    try:
        response = model.generate_content(user_prompt)
        if not response.text:
            raise RuntimeError("Gemini failed to generate content")
        
        # Prepare new version data
        rewritten_data = {
            "book_title": metadata["book_title"],
            "author": metadata["author"],
            "chapter_info": metadata["chapter_info"],
            "chapter_title": f"Rewritten: {metadata['chapter_title']}",
            "content": response.text,
            "source_url": metadata["source_url"]
        }
        
        return rewritten_data
    
    except Exception as e:
        print(f"Error generating content: {str(e)}")
        if "quota" in str(e).lower():
            print("Waiting 60 seconds before retrying...")
            time.sleep(60)
            return rewrite_chapter(versioned_id, special_instructions)
        raise

def process_rewrite(base_id: str, special_instructions: str = "None"):
    """
    Complete rewrite workflow:
    1. Fetches latest raw version
    2. Generates AI rewrite
    3. Saves new version to ChromaDB
    """
    # Get latest raw version
    latest_raw_id = f"{base_id}_ver{get_latest_version(base_id, 'raw')}"
    
    # Generate rewrite
    rewritten_data = rewrite_chapter(latest_raw_id, special_instructions)
    
    # Save as new "rewritten" stage version
    save_chapter_auto_version(
        data=rewritten_data,
        base_id=base_id,
        stage="rewritten"
    )
    
    print(f"Successfully rewritten and saved as new version of {base_id}")

if __name__ == "__main__":
    try:
        process_rewrite(
            base_id="chapter1",
            special_instructions="Emphasize the atmospheric descriptions of the setting"
        )
    except Exception as e:
        print(f"Error in rewrite process: {str(e)}")