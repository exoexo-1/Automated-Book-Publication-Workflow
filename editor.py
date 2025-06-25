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

latest_version_raw = get_latest_version("chapter1", "raw")
latest_version_reviewed = get_latest_version("chapter1", "reviewed")

if latest_version_raw == 0 or latest_version_reviewed == 0:
    raise ValueError("Missing raw or reviewed version in ChromaDB.")

versioned_id_raw = f"chapter1_ver{latest_version_raw}"
raw_data = fetch_chapter_by_version(versioned_id_raw, "raw")

versioned_id_reviewed = f"chapter1_ver{latest_version_reviewed}"
reviewed_data = fetch_chapter_by_version(versioned_id_reviewed, "reviewed")

def editor(raw_data, reviewed_data):
    book_title = raw_data["metadata"].get("book_title", "Untitled")
    author = raw_data["metadata"].get("author", "Untitled")
    chapter_title = raw_data["metadata"].get("chapter_title", "Untitled")
    raw_text = raw_data["content"]
    reviewed_text = reviewed_data["content"]
    reviewer_feedback = reviewed_data["metadata"].get("reviewer_feedback", "None provided")

    EDITOR_SYSTEM_PROMPT = textwrap.dedent(f"""
        You are a professional book EDITOR working with the following REVIEWER FEEDBACK on rewritten(spinning) content of a book chapter:
        ---
        {reviewer_feedback}
        ---
        Your task is to revise the rewritten chapter while strictly following reviewer's feedback.
    """)

    EDITOR_USER_PROMPT = textwrap.dedent(f"""
        ### Chapter Revision Task
        **Title**: {chapter_title}
        **Book**: {book_title}
        **Author**: {author}
        
        ### Reviewer Feedback:
        {reviewer_feedback}
        
        ### Original Text (Reference):
        {raw_text}
        
        ### Current Rewritten Version (To Edit):
        {reviewed_text}
        
        Please provide your revised version that addresses all reviewer concerns.
        Return ONLY the revised text, no additional commentary.
    """)

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=EDITOR_SYSTEM_PROMPT
    )

    try:
        response = model.generate_content(EDITOR_USER_PROMPT)
        if not response.text:
            raise RuntimeError("Gemini failed to generate content")
        return response.text

    except Exception as e:
        print(f"Error generating revision: {str(e)}")
        if "quota" in str(e).lower():
            print("Waiting 60 seconds before retrying...")
            time.sleep(60)
            return editor(raw_data, reviewed_data)
        raise

# Call editor function
edited_content = editor(raw_data, reviewed_data)

def editor_save():
    save_chapter_auto_version(
        data={
            **reviewed_data["metadata"],
            "content": edited_content,
            "reviewer_feedback": reviewed_data["metadata"].get("reviewer_feedback", "")
        },
        base_id="chapter1",
        stage="edited"
    )

editor_save()

# Fetch and display the saved edited version
latest_version_edited = get_latest_version("chapter1", "edited")
versioned_id_edited = f"chapter1_ver{latest_version_edited}"
edited_data = fetch_chapter_by_version(versioned_id_edited, "edited")
print("\n\n\n", edited_data)
