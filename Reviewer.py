from save import save_chapter_auto_version, get_latest_version, fetch_chapter_by_version, format_chapter_markdown
import os
from dotenv import load_dotenv
from openai import OpenAI
import textwrap
import time

load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    raise EnvironmentError(" OPENAI_API_KEY not set in .env")

openai = OpenAI(api_key=openai_api_key)

latest_version_raw = get_latest_version("chapter1", "raw")
latest_version_rewritten = get_latest_version("chapter1", "rewritten")

if latest_version_raw == 0 or latest_version_rewritten == 0:
    raise ValueError("Missing raw or rewritten version in ChromaDB.")

versioned_id_raw = f"chapter1_ver{latest_version_raw}"
versioned_id_rewritten = f"chapter1_ver{latest_version_rewritten}"

raw_data = fetch_chapter_by_version(versioned_id_raw, "raw")
rewritten_data = fetch_chapter_by_version(versioned_id_rewritten, "rewritten")

# print(rewritten_data)
# print(raw_data)

if not raw_data or not rewritten_data:
    raise ValueError("Failed to fetch both raw and rewritten versions.")

def reviwer(raw_data,rewritten_data):
    raw_text = raw_data["content"]
    rewritten_text = rewritten_data["content"]
    chapter_title = raw_data["metadata"].get("chapter_title", "Untitled")

    raw_word_count = len(raw_text.split())
    rewritten_word_count = len(rewritten_text.split())

    REVIEWER_SYSTEM_PROMPT = textwrap.dedent(f"""
        You are a senior literary reviewer evaluating rewritten chapters for publication readiness. The rewritten version should be a polished improvement over the original, not a strict copy.

        You must assess:

        1. **Meaning Preservation**:  
        - All core plot points, character actions, and important themes must remain intact.
        - Do NOT approve if major events are missing, changed, or fabricated.

        2. **Tone & Style**:  
        - Maintain a literary, slightly formal tone.  
        - Language should feel natural, elegant, and reader-friendly.

        3. **Dialogue & Flow**:  
        - Dialogue must preserve character intent and be improved for naturalness.  
        - Narrative flow should feel smoother than the original.

        4. **Structure & Pacing**:  
        - Slight restructuring is allowed if it improves pacing or clarity.  
        - Paragraph breaks, sentence variation, and transitions should aid readability.

        5. **Technical Quality**:  
        - Grammar, punctuation, and syntax must be error-free.  
        - Word count deviation of ±10% is acceptable if it enhances clarity, flow, or readability.

        Your job is NOT to reject over minor differences. Only reject if there are **serious integrity issues**.

        ---

        Respond in one of the following formats:

        [VERIFIED]  
        Suggested improvements:  
        - <concise list of stylistic or polish suggestions, if any>

        OR

        [NOT VERIFIED]  
        Key issues:  
        - <critical problem 1> (detailed) 
        - <critical problem 2> (with fix idea)


    """)


    REVIEWER_USER_PROMPT = textwrap.dedent(f"""
        ### Chapter: "{chapter_title}" 
        **Original Word Count**: {raw_word_count}
        **Rewritten Word Count**: {rewritten_word_count}

        ---

        ### ORIGINAL TEXT (Raw):
        {raw_text}

        ---

        ### REWRITTEN TEXT:
        {rewritten_text}

        
    """)


    # --- STEP 3: Call OpenAI ---
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
            {"role": "user", "content": REVIEWER_USER_PROMPT}
        ]
    )

    result = response.choices[0].message.content

    return result


# reviewer_feedback = reviwer(raw_data, rewritten_data)
# print("AI Verification Result:\n")
# print(reviewer_feedback)

def reviwer_save():
    save_chapter_auto_version(
        data={
            **rewritten_data["metadata"],
            "content": rewritten_data["content"],
            "reviewer_feedback": reviewer_feedback
        },
        base_id="chapter1",
        stage="reviewed" 
    )

# reviwer_save() 

# latest_version_reviewed = get_latest_version("chapter1", "reviewed")
# versioned_id_reviewed = f"chapter1_ver{latest_version_reviewed}"
# reviewed_data = fetch_chapter_by_version(versioned_id_reviewed, "reviewed")
# print("\n\n\n", format_chapter_markdown(reviewed_data))