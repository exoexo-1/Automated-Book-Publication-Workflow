from save import save_chapter_auto_version, get_latest_version, fetch_chapter_by_version, format_chapter_markdown
import google.generativeai as genai
import os
from dotenv import load_dotenv
import textwrap
import time

# Load environment variables
# load_dotenv(override=True)
# google_api_key = os.getenv('GOOGLE_API_KEY')

# if not google_api_key:
#     raise ValueError("Google API Key not set in environment variables")

# # Configure Gemini
# genai.configure(api_key=google_api_key)

# latest_version_raw = get_latest_version("chapter1", "raw")

# if latest_version_raw == 0:
#     raise ValueError("Missing raw version in ChromaDB.")

# versioned_id_raw = f"chapter1_ver{latest_version_raw}"
# raw_data = fetch_chapter_by_version(versioned_id_raw, "raw")



def rewriter(raw_data, special_instructions: str = "None"):
    book_title = raw_data["metadata"].get("book_title", "Untitled")
    author = raw_data["metadata"].get("author", "Untitled")
    chapter_title = raw_data["metadata"].get("chapter_title", "Untitled")
    raw_text = raw_data["content"]
    word_count = len(raw_text.split())

    
    REWRITER_SYSTEM_PROMPT = textwrap.dedent(f"""
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
        - Target word count should be ±8% of original
    """)

    REWRITER_USER_PROMPT = textwrap.dedent(f"""
        Rewrite this chapter while following all guidelines above:
        
        --- CHAPTER METADATA ---
        Title: {chapter_title}
        From Book: {book_title}
        Author: {author}
        Original Word Count: {word_count}
        
        --- CONTENT TO REWRITE ---
        {raw_text}
        
        --- SPECIAL INSTRUCTIONS ---
        {special_instructions}
    """)

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=REWRITER_SYSTEM_PROMPT
    )

    try:
        response = model.generate_content(REWRITER_USER_PROMPT)
        if not response.text:
            raise RuntimeError("Gemini failed to generate content")
        
        rewritten_data = {
            "book_title": book_title,
            "author": author,
            "chapter_info": raw_data["metadata"].get("chapter_info", ""),
            "chapter_title": f"Rewritten: {chapter_title}",
            "content": response.text,
            "source_url": raw_data["metadata"].get("source_url", "")
        }
        
        return rewritten_data

    except Exception as e:
        print(f"Error generating revision: {str(e)}")
        if "quota" in str(e).lower():
            print("Waiting 60 seconds before retrying...")
            time.sleep(60)
            return rewriter(raw_data, special_instructions)
        raise

# Call rewriter function with special instructions
# rewritten_content = rewriter(raw_data, special_instructions="Emphasize the atmospheric descriptions of the setting")

def rewriter_save():
    save_chapter_auto_version(
        data=rewritten_content,
        base_id="chapter1",
        stage="rewritten"
    )

# rewriter_save()

# # Fetch and display the saved rewritten version
# latest_version_rewritten = get_latest_version("chapter1", "rewritten")
# versioned_id_rewritten = f"chapter1_ver{latest_version_rewritten}"
# rewritten_data = fetch_chapter_by_version(versioned_id_rewritten, "rewritten")
# print("\n\n\n", format_chapter_markdown(rewritten_data))