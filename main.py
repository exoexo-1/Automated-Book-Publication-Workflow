from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from save import save_chapter_auto_version, get_latest_version, fetch_chapter_by_version, format_chapter_markdown
from Reviewer import reviwer
from editor import editor
from Rewriter import rewriter
import google.generativeai as genai
import os
from dotenv import load_dotenv
import textwrap
import time
from openai import OpenAI
import tempfile
import subprocess

# Load environment variables
load_dotenv(override=True)

# Configure Gemini
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    raise ValueError("Google API Key not set in environment variables")
genai.configure(api_key=google_api_key)

def edit_in_system_editor(content):
    """Edit content using system's default text editor"""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode='w+', delete=False, encoding='utf-8') as tf:
        tf.write(content)
        tf.flush()
        temp_path = tf.name
    
    # Get system editor (try common env vars first)
    editor = os.getenv('EDITOR') or os.getenv('VISUAL') or 'nano'  # Default to nano if nothing set
    
    try:
        subprocess.call([editor, temp_path])
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            edited_content = f.read()
        
        os.unlink(temp_path)
        return edited_content
    except Exception as e:
        print(f"Error editing file: {e}")
        try:
            os.unlink(temp_path)
        except:
            pass
        return None

def human_edit_content(current_content, stage):
    """Enhanced content editing with proper editor and preview options"""
    while True:
        print(f"\n{'='*20} {stage.upper()} CONTENT {'='*20}")
        print(current_content)
        print("="*50)
        
        print("\nEditing options:")
        print("1. Edit content (opens in text editor)")
        print("2. Preview current version")
        print("3. Save and finish editing")
        print("4. Cancel editing")
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice == "1":
            edited_content = edit_in_system_editor(current_content)
            if edited_content is not None:
                current_content = edited_content
        elif choice == "2":
            continue  # Just shows content again
        elif choice == "3":
            return current_content
        elif choice == "4":
            return None
        else:
            print("⚠️ Invalid choice, please try again")

def get_human_decision(prompt, options):
    print("\n" + "="*50)
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}⃣  {option['description']}")
    print("="*50)

    while True:
        choice = input(f"Enter option (1-{len(options)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice)-1]['action']
        print("⚠️ Invalid choice. Please try again.")

def process_rewriting():
    latest_version_raw = get_latest_version("chapter1", "raw")
    versioned_id_raw = f"chapter1_ver{latest_version_raw}"
    raw_data = fetch_chapter_by_version(versioned_id_raw, "raw")

    special_instruction = input("\nEnter any special instruction for AI rewriter or press ENTER to skip: ")
    if not special_instruction:
        special_instruction = "None"

    rewritten_content = rewriter(raw_data, special_instruction)

    print("\nAI Rewritten Content:")
    print("="*50)
    print(format_chapter_markdown({"content": rewritten_content["content"], "metadata": rewritten_content}))
    print("="*50)

    while True:
        decision = get_human_decision(
            "How would you like to proceed with the rewritten content?",
            [
                {"description": "Accept as-is and proceed to AI reviewer", "action": "proceed"},
                {"description": "Edit the content manually before proceeding", "action": "edit"},
                {"description": "Save as final version and exit", "action": "finalize"}
            ]
        )

        if decision == "edit":
            edited_content = human_edit_content(rewritten_content["content"], "rewritten")
            if edited_content is None:
                continue  # User cancelled editing
            rewritten_content["content"] = edited_content
            
            # Ask if user wants to save
            save_decision = get_human_decision(
                "Save this edited version?",
                [
                    {"description": "Yes, save as human-edited version", "action": "save"},
                    {"description": "No, continue editing", "action": "edit_again"},
                    {"description": "Cancel and go back", "action": "cancel"}
                ]
            )
            
            if save_decision == "save":
                save_chapter_auto_version(data=rewritten_content, base_id="chapter1", stage="human_rewritten")
                print("\n✅ Saved human-edited rewritten version.")
                return "human_rewritten"
            elif save_decision == "edit_again":
                continue
            else:
                continue
                
        elif decision == "finalize":
            save_chapter_auto_version(data=rewritten_content, base_id="chapter1", stage="final")
            print("\n✅ Saved as final version. Exiting.")
            return "final"
        else:
            save_chapter_auto_version(data=rewritten_content, base_id="chapter1", stage="rewritten")
            print("\n✅ Saved AI-rewritten version. Proceeding to reviewer.")
            return "rewritten"

def process_reviewing(previous_stage):
    latest_version = get_latest_version("chapter1", previous_stage)
    versioned_id = f"chapter1_ver{latest_version}"
    rewritten_data = fetch_chapter_by_version(versioned_id, previous_stage)

    latest_version_raw = get_latest_version("chapter1", "raw")
    versioned_id_raw = f"chapter1_ver{latest_version_raw}"
    raw_data = fetch_chapter_by_version(versioned_id_raw, "raw")

    reviewer_feedback = reviwer(raw_data, rewritten_data)

    print("\nAI Reviewer Feedback:")
    print("="*50)
    print(reviewer_feedback)
    print("="*50)

    while True:
        decision = get_human_decision(
            "How would you like to proceed with the reviewer feedback?",
            [
                {"description": "Accept feedback and proceed to AI editor", "action": "proceed"},
                {"description": "Edit the feedback before proceeding", "action": "edit_feedback"},
                {"description": "Save as final version and exit", "action": "finalize"}
            ]
        )

        if decision == "edit_feedback":
            edited_feedback = human_edit_content(reviewer_feedback, "reviewer_feedback")
            if edited_feedback is None:
                continue
                
            save_decision = get_human_decision(
                "Save this edited feedback?",
                [
                    {"description": "Yes, save and proceed", "action": "save"},
                    {"description": "No, edit again", "action": "edit_again"},
                    {"description": "Cancel", "action": "cancel"}
                ]
            )
            
            if save_decision == "save":
                save_chapter_auto_version(
                    data={**rewritten_data["metadata"], "content": rewritten_data["content"], "reviewer_feedback": edited_feedback},
                    base_id="chapter1",
                    stage="human_reviewed"
                )
                print("\n✅ Saved human-edited reviewer feedback. Proceeding to editor.")
                return "human_reviewed"
            elif save_decision == "edit_again":
                reviewer_feedback = edited_feedback
                continue
            else:
                continue
                
        elif decision == "finalize":
            save_chapter_auto_version(
                data={**rewritten_data["metadata"], "content": rewritten_data["content"], "reviewer_feedback": reviewer_feedback},
                base_id="chapter1",
                stage="final"
            )
            print("\n✅ Saved as final version. Exiting.")
            return "final"
        else:
            save_chapter_auto_version(
                data={**rewritten_data["metadata"], "content": rewritten_data["content"], "reviewer_feedback": reviewer_feedback},
                base_id="chapter1",
                stage="reviewed"
            )
            print("\n✅ Saved AI-reviewed version. Proceeding to editor.")
            return "reviewed"

def process_editing(reviewed_stage):
    latest_version = get_latest_version("chapter1", reviewed_stage)
    versioned_id = f"chapter1_ver{latest_version}"
    reviewed_data = fetch_chapter_by_version(versioned_id, reviewed_stage)

    latest_version_raw = get_latest_version("chapter1", "raw")
    versioned_id_raw = f"chapter1_ver{latest_version_raw}"
    raw_data = fetch_chapter_by_version(versioned_id_raw, "raw")

    edited_content = editor(raw_data, reviewed_data)

    print("\nAI Edited Content:")
    print("="*50)
    print(format_chapter_markdown({"content": edited_content, "metadata": reviewed_data["metadata"]}))
    print("="*50)

    while True:
        decision = get_human_decision(
            "How would you like to proceed with the edited content?",
            [
                {"description": "Accept as final version", "action": "finalize"},
                {"description": "Edit the content manually before finalizing", "action": "edit"},
                {"description": "Send back to reviewer for another round", "action": "review_again"}
            ]
        )

        if decision == "edit":
            edited_content = human_edit_content(edited_content, "edited_content")
            if edited_content is None:
                continue
                
            save_decision = get_human_decision(
                "Save this edited version?",
                [
                    {"description": "Yes, save as human-edited version", "action": "save"},
                    {"description": "No, continue editing", "action": "edit_again"},
                    {"description": "Cancel", "action": "cancel"}
                ]
            )
            
            if save_decision == "save":
                # Create proper data structure for saving
                save_data = {
                    "book_title": reviewed_data["metadata"]["book_title"],
                    "author": reviewed_data["metadata"]["author"],
                    "chapter_info": reviewed_data["metadata"]["chapter_info"],
                    "chapter_title": reviewed_data["metadata"]["chapter_title"],
                    "content": edited_content,
                    "source_url": reviewed_data["metadata"]["source_url"],
                    "reviewer_feedback": reviewed_data["metadata"].get("reviewer_feedback", "")
                }
                
                save_chapter_auto_version(data=save_data, base_id="chapter1", stage="human_edited")
                print("\n✅ Saved human-edited version.")

                final_decision = get_human_decision(
                    "Would you like to:",
                    [
                        {"description": "Finalize this version", "action": "finalize"},
                        {"description": "Send back to reviewer", "action": "review_again"}
                    ]
                )

                if final_decision == "finalize":
                    save_chapter_auto_version(data=save_data, base_id="chapter1", stage="final")
                    print("\n✅ Saved as final version. Exiting.")
                    return "final"
                else:
                    return "human_edited"
                    
            elif save_decision == "edit_again":
                continue
            else:
                continue
                
        elif decision == "finalize":
            # Create proper data structure for saving
            save_data = {
                "book_title": reviewed_data["metadata"]["book_title"],
                "author": reviewed_data["metadata"]["author"],
                "chapter_info": reviewed_data["metadata"]["chapter_info"],
                "chapter_title": reviewed_data["metadata"]["chapter_title"],
                "content": edited_content,
                "source_url": reviewed_data["metadata"]["source_url"],
                "reviewer_feedback": reviewed_data["metadata"].get("reviewer_feedback", "")
            }
            save_chapter_auto_version(data=save_data, base_id="chapter1", stage="final")
            print("\n✅ Saved as final version. Exiting.")
            return "final"
        else:
            # Create proper data structure for saving
            save_data = {
                "book_title": reviewed_data["metadata"]["book_title"],
                "author": reviewed_data["metadata"]["author"],
                "chapter_info": reviewed_data["metadata"]["chapter_info"],
                "chapter_title": reviewed_data["metadata"]["chapter_title"],
                "content": edited_content,
                "source_url": reviewed_data["metadata"]["source_url"],
                "reviewer_feedback": reviewed_data["metadata"].get("reviewer_feedback", "")
            }
            save_chapter_auto_version(data=save_data, base_id="chapter1", stage="edited")
            print("\n✅ Saved AI-edited version. Sending back to reviewer.")
            return "edited"
def main():
    latest_version_raw = get_latest_version("chapter1", "raw")
    versioned_id_raw = f"chapter1_ver{latest_version_raw}"
    raw_data = fetch_chapter_by_version(versioned_id_raw, "raw")
    print("\nInitial content saved as raw version.")
    print("\n" + format_chapter_markdown(raw_data))

    rewritten_stage = process_rewriting()
    if rewritten_stage == "final":
        return

    reviewed_stage = process_reviewing(rewritten_stage)
    if reviewed_stage == "final":
        return

    while True:
        edited_stage = process_editing(reviewed_stage)
        if edited_stage == "final":
            break
        elif edited_stage == "human_edited":
            reviewed_stage = process_reviewing("human_edited")
            if reviewed_stage == "final":
                break
        else:
            reviewed_stage = process_reviewing("edited")
            if reviewed_stage == "final":
                break

    latest_version_final = get_latest_version("chapter1", "final")
    versioned_id_final = f"chapter1_ver{latest_version_final}"
    final_data = fetch_chapter_by_version(versioned_id_final, "final")

    print("\n🎉 Final Version:")
    print("="*50)
    print(format_chapter_markdown(final_data))
    print("="*50)

if __name__ == "__main__":
    main()