from save import save_chapter_auto_version, get_latest_version, fetch_chapter_by_version
from Reviewer import reviwer
import google.generativeai as genai
import os
from dotenv import load_dotenv
import textwrap
import time



def manage_reviewer_answer(result_text: str, chapter_title: str, versioned_id: str):
    print("\n===================== REVIEWER STATUS =====================")
    
    if "[VERIFIED]" in result_text.upper():
        print(f"\n✅ AI Verification Passed for chapter: {chapter_title}")
        print("\nAI suggested improvements (if any):\n")
        print(result_text)
        
        print("\nWhat would you like to do next?")
        print("1️⃣  Apply additional AI improvements based on suggestions")
        print("2️⃣  Manually edit the rewritten chapter")
        print("3️⃣  Finalize for publication and save")

        choice = input("Enter option (1/2/3): ").strip()

        if choice == "1":
            print("\n➡️ Proceeding to AI editor with AI suggestions...\n")
            return "ai_editor_suggestions"
        
        elif choice == "2":
            print("\n📝 Launching manual editor for rewritten content...\n")
            return "manual_edit"
        
        elif choice == "3":
            print(f"\n📦 Finalizing version {versioned_id} for publication...\n")
            return "finalize"
        
        else:
            print("⚠️ Invalid choice. Skipping action.")
            return "skip"

    elif "[NOT VERIFIED]" in result_text.upper():
        print(f"\n❌ AI Verification Could Not Pass for chapter: {chapter_title}")
        print("\nAI Verification Result:\n")
        print("--------------------------------------------------")
        print(result_text)
        print("--------------------------------------------------")

        print("\nHow would you like to proceed?")
        print("1️⃣  Proceed to AI Editor without manual fix")
        print("2️⃣  Edit the AI-suggested fixes and then go to AI Editor")
        print("3️⃣  Manually fix the rewritten chapter")
        print("4️⃣  Skip and finalize as-is (not recommended)")

        choice = input("Enter option (1/2/3/4): ").strip()

        if choice == "1":
            print("\n➡️ Proceeding to AI editor without applying reviewer fixes...\n")
            return "ai_editor_direct"
        
        elif choice == "2":
            print("\n🛠️ Editing AI-suggested fixes before continuing...\n")
            return "edit_then_ai_editor"
        
        elif choice == "3":
            print("\n📝 Opening manual editor for full control...\n")
            return "manual_edit"
        
        elif choice == "4":
            print("\n⚠️ Skipping review stage and finalizing as-is...\n")
            return "finalize"
        
        else:
            print("⚠️ Invalid choice. Skipping action.")
            return "skip"

    else:
        print("⚠️ Unable to determine verification status from AI response.")
        print(result_text)
        return "error"
