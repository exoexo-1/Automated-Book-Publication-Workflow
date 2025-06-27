import gradio as gr
from ScreenShot_scrapper import extract_chapter_info
from save import save_chapter_auto_version, get_latest_version, fetch_chapter_by_version, format_chapter_markdown, get_next_version
from Rewriter import rewriter
from Reviewer import reviwer
from editor import editor

STATE = {
    "current_stage": "init",
    "raw_data": None,
    "rewritten_data": None,
    "reviewed_data": None,
    "edited_data": None,
    "special_instruction": "None",
    "editing_content": False,
    "editing_feedback": False
}

def fetch_chapter(url):
    """Fetch chapter from Wikisource URL"""
    if not url or not url.startswith("https://en.wikisource.org/wiki"):
        return (
            gr.update(value="❌ Invalid URL! Please use a valid Wikisource URL."),
            gr.update(value=""),  # feedback_output
            *[gr.update(visible=False)] * 9  # All buttons
        )
    
    try:
        data = extract_chapter_info(url)
        save_chapter_auto_version({
            **data,
            "reviewer_feedback": ""
        }, base_id="chapter1", stage="raw")

        STATE["raw_data"] = {
            "content": data["content"],
            "metadata": {**data, "version": get_latest_version("chapter1", "raw"), "stage": "raw", 
                        "versioned_id": f"chapter1_ver{get_latest_version('chapter1', 'raw')}", 
                        "reviewer_feedback": ""}
        }
        STATE["current_stage"] = "raw"

        return (
            format_chapter_markdown(STATE["raw_data"]),
            gr.update(value=""),  # feedback_output
            gr.update(visible=True),   # rewrite_btn
            gr.update(visible=True),   # rewrite_special_btn
            gr.update(visible=False),  # rewrite_again_btn
            gr.update(visible=False),  # reviewer_btn
            gr.update(visible=False),  # editor_btn
            gr.update(visible=False),  # edit_btn
            gr.update(visible=False),  # edit_feedback_btn
            gr.update(visible=False),  # finalize_btn
            gr.update(visible=False)   # status_output
        )
    except Exception as e:
        return (
            gr.update(value=f"❌ Error fetching chapter: {str(e)}"),
            gr.update(value=""),
            *[gr.update(visible=False)] * 9
        )

def rewrite_chapter(use_special):
    """Handle chapter rewriting"""
    if STATE["raw_data"] is None:
        latest = get_latest_version("chapter1", "raw")
        if latest == 0:
            return (
                gr.update(value="❌ No raw data found!"),
                gr.update(value=""),
                *[gr.update(visible=False)] * 9
            )
        STATE["raw_data"] = fetch_chapter_by_version(f"chapter1_ver{latest}", "raw")

    if use_special:
        # Show special instructions input
        return (
            STATE["raw_data"] and format_chapter_markdown(STATE["raw_data"]) or "No data",
            gr.update(value=""),
            gr.update(visible=False),  # rewrite_btn
            gr.update(visible=False),  # rewrite_special_btn
            gr.update(visible=False),  # rewrite_again_btn
            gr.update(visible=False),  # reviewer_btn
            gr.update(visible=False),  # editor_btn
            gr.update(visible=False),  # edit_btn
            gr.update(visible=False),  # edit_feedback_btn
            gr.update(visible=False),  # finalize_btn
            gr.update(visible=True)    # status_output - will be used to show special instruction input
        )
    else:
        try:
            result = rewriter(STATE["raw_data"], "None")
            rewritten_content = {
                "content": result["content"],
                "metadata": {**STATE["raw_data"]["metadata"], **result, "reviewer_feedback": ""}
            }
            STATE["rewritten_data"] = rewritten_content
            STATE["current_stage"] = "rewritten"
            save_chapter_auto_version({**rewritten_content["metadata"], "content": result["content"]}, "chapter1", "rewritten")

            return (
                format_chapter_markdown(rewritten_content),
                gr.update(value=""),
                gr.update(visible=False),  # rewrite_btn
                gr.update(visible=False),  # rewrite_special_btn
                gr.update(visible=True),   # rewrite_again_btn
                gr.update(visible=True),   # reviewer_btn
                gr.update(visible=False),  # editor_btn
                gr.update(visible=True),   # edit_btn
                gr.update(visible=False),  # edit_feedback_btn
                gr.update(visible=True),   # finalize_btn
                gr.update(visible=False)   # status_output
            )
        except Exception as e:
            return (
                gr.update(value=f"❌ Error during rewriting: {str(e)}"),
                gr.update(value=""),
                *[gr.update(visible=False)] * 9
            )

def save_special_instruction(instr):
    """Save special instruction and rewrite"""
    STATE["special_instruction"] = instr or "None"
    try:
        result = rewriter(STATE["raw_data"], instr or "None")
        rewritten_content = {
            "content": result["content"],
            "metadata": {**STATE["raw_data"]["metadata"], **result, "reviewer_feedback": ""}
        }
        STATE["rewritten_data"] = rewritten_content
        STATE["current_stage"] = "rewritten"
        save_chapter_auto_version({**rewritten_content["metadata"], "content": result["content"]}, "chapter1", "rewritten")

        return (
            format_chapter_markdown(rewritten_content),
            gr.update(value=""),
            gr.update(visible=False),  # rewrite_btn
            gr.update(visible=False),  # rewrite_special_btn
            gr.update(visible=True),   # rewrite_again_btn
            gr.update(visible=True),   # reviewer_btn
            gr.update(visible=False),  # editor_btn
            gr.update(visible=True),   # edit_btn
            gr.update(visible=False),  # edit_feedback_btn
            gr.update(visible=True),   # finalize_btn
            gr.update(visible=False)   # status_output
        )
    except Exception as e:
        return (
            gr.update(value=f"❌ Error during special rewrite: {str(e)}"),
            gr.update(value=""),
            *[gr.update(visible=False)] * 9
        )

def rewrite_again():
    """Reset to raw stage for rewriting"""
    if STATE["raw_data"] is None:
        latest = get_latest_version("chapter1", "raw")
        if latest == 0:
            return (
                gr.update(value="❌ No raw data found!"),
                gr.update(value=""),
                *[gr.update(visible=False)] * 9
            )
        STATE["raw_data"] = fetch_chapter_by_version(f"chapter1_ver{latest}", "raw")

    STATE["current_stage"] = "raw"
    return (
        format_chapter_markdown(STATE["raw_data"]),
        gr.update(value=""),
        gr.update(visible=True),   # rewrite_btn
        gr.update(visible=True),   # rewrite_special_btn
        gr.update(visible=False),  # rewrite_again_btn
        gr.update(visible=False),  # reviewer_btn
        gr.update(visible=False),  # editor_btn
        gr.update(visible=False),  # edit_btn
        gr.update(visible=False),  # edit_feedback_btn
        gr.update(visible=False),  # finalize_btn
        gr.update(visible=False)   # status_output
    )

def review_chapter():
    """Handle review stage - intelligently determines what data to review based on current state"""
    try:
        # Get raw data first (always needed as reference)
        latest_raw = get_latest_version("chapter1", "raw")
        if latest_raw == 0:
            return (
                gr.update(value="❌ No raw data found!"),
                gr.update(value=""),
                *[gr.update(visible=False)] * 9
            )
        raw_data = fetch_chapter_by_version(f"chapter1_ver{latest_raw}", "raw")
        if not STATE["raw_data"]:
            STATE["raw_data"] = raw_data

        # Determine what data to review based on current state and available versions
        data_to_review = None
        
        if STATE["current_stage"] == "edited" and STATE["edited_data"]:
            # Currently in edited stage - review the edited content
            data_to_review = STATE["edited_data"]
        elif STATE["current_stage"] == "rewritten" and STATE["rewritten_data"]:
            # Currently in rewritten stage - review the rewritten content
            data_to_review = STATE["rewritten_data"]
        else:
            # State is unclear, determine from database what's the latest to review
            # Priority: human_edited > edited > human_rewritten > rewritten
            
            stages_to_check = ["human_edited", "edited", "human_rewritten", "rewritten"]
            latest_data = None
            latest_version = 0
            
            for stage in stages_to_check:
                version = get_latest_version("chapter1", stage)
                if version > 0:
                    temp_data = fetch_chapter_by_version(f"chapter1_ver{version}", stage)
                    if temp_data and version > latest_version:
                        latest_data = temp_data
                        latest_version = version
                        break  # Take the first (highest priority) stage found
            
            if not latest_data:
                return (
                    gr.update(value="❌ No rewritten/edited data found to review!"),
                    gr.update(value=""),
                    *[gr.update(visible=False)] * 9
                )
            
            data_to_review = latest_data

        # Generate feedback using the reviewer
        feedback = reviwer(raw_data, data_to_review)
        
        # Create proper version for reviewed data
        next_version = get_next_version("chapter1")
        STATE["reviewed_data"] = {
            "content": data_to_review["content"],
            "metadata": {
                "book_title": data_to_review["metadata"]["book_title"],
                "author": data_to_review["metadata"]["author"],
                "chapter_info": data_to_review["metadata"]["chapter_info"],
                "chapter_title": data_to_review["metadata"]["chapter_title"],
                "source_url": data_to_review["metadata"]["source_url"],
                "reviewer_feedback": feedback,
                "version": next_version,
                "stage": "reviewed",
                "versioned_id": f"chapter1_ver{next_version}",
                "reviewed_from_stage": data_to_review["metadata"].get("stage", "unknown")  # Track what stage was reviewed
            }
        }
        STATE["current_stage"] = "reviewed"
        
        # Save the reviewed version
        save_chapter_auto_version(
            data={
                "book_title": STATE["reviewed_data"]["metadata"]["book_title"],
                "author": STATE["reviewed_data"]["metadata"]["author"],
                "chapter_info": STATE["reviewed_data"]["metadata"]["chapter_info"],
                "chapter_title": STATE["reviewed_data"]["metadata"]["chapter_title"],
                "content": STATE["reviewed_data"]["content"],
                "source_url": STATE["reviewed_data"]["metadata"]["source_url"],
                "reviewer_feedback": feedback
            },
            base_id="chapter1",
            stage="reviewed"
        )
        
        return (
            format_chapter_markdown(STATE["reviewed_data"]),
            feedback,
            gr.update(visible=False),  # rewrite_btn
            gr.update(visible=False),  # rewrite_special_btn
            gr.update(visible=True),   # rewrite_again_btn
            gr.update(visible=False),  # reviewer_btn
            gr.update(visible=True),   # editor_btn
            gr.update(visible=True),   # edit_btn
            gr.update(visible=True),   # edit_feedback_btn
            gr.update(visible=True),   # finalize_btn
            gr.update(visible=False)   # status_output
        )
    except Exception as e:
        return (
            gr.update(value=f"❌ Error during review: {str(e)}"),
            gr.update(value=""),
            *[gr.update(visible=False)] * 9
        )
    
def edit_with_feedback():
    """Perform AI editing based on feedback"""
    try:
        latest_raw = get_latest_version("chapter1", "raw")
        if latest_raw == 0:
            return (
                gr.update(value="❌ No raw data found!"),
                gr.update(value=""),
                *[gr.update(visible=False)] * 9
            )
        raw_data = fetch_chapter_by_version(f"chapter1_ver{latest_raw}", "raw")
        if not STATE["raw_data"]:
            STATE["raw_data"] = raw_data
        
        if STATE["reviewed_data"] is None:
            latest_reviewed = get_latest_version("chapter1", "reviewed")
            if latest_reviewed == 0:
                return (
                    gr.update(value="❌ No reviewed data found!"),
                    gr.update(value=""),
                    *[gr.update(visible=False)] * 9
                )
            reviewed_data = fetch_chapter_by_version(f"chapter1_ver{latest_reviewed}", "reviewed")
            STATE["reviewed_data"] = reviewed_data

        edited_content = editor(raw_data, STATE["reviewed_data"])
        
        # Create proper version for edited data
        next_version = get_next_version("chapter1")
        STATE["edited_data"] = {
            "content": edited_content,
            "metadata": {
                "book_title": STATE["reviewed_data"]["metadata"]["book_title"],
                "author": STATE["reviewed_data"]["metadata"]["author"],
                "chapter_info": STATE["reviewed_data"]["metadata"]["chapter_info"],
                "chapter_title": STATE["reviewed_data"]["metadata"]["chapter_title"],
                "source_url": STATE["reviewed_data"]["metadata"]["source_url"],
                "reviewer_feedback": STATE["reviewed_data"]["metadata"]["reviewer_feedback"],
                "version": next_version,
                "stage": "edited",
                "versioned_id": f"chapter1_ver{next_version}"
            }
        }
        STATE["current_stage"] = "edited"
        
        save_chapter_auto_version(
            data={
                "book_title": STATE["edited_data"]["metadata"]["book_title"],
                "author": STATE["edited_data"]["metadata"]["author"],
                "chapter_info": STATE["edited_data"]["metadata"]["chapter_info"],
                "chapter_title": STATE["edited_data"]["metadata"]["chapter_title"],
                "content": edited_content,
                "source_url": STATE["edited_data"]["metadata"]["source_url"],
                "reviewer_feedback": STATE["edited_data"]["metadata"]["reviewer_feedback"]
            },
            base_id="chapter1",
            stage="edited"
        )
        
        return (
            format_chapter_markdown(STATE["edited_data"]),
            STATE["edited_data"]["metadata"]["reviewer_feedback"],
            gr.update(visible=False),  # rewrite_btn
            gr.update(visible=False),  # rewrite_special_btn
            gr.update(visible=True),   # rewrite_again_btn
            gr.update(visible=True),   # reviewer_btn
            gr.update(visible=False),  # editor_btn
            gr.update(visible=True),   # edit_btn
            gr.update(visible=True),   # edit_feedback_btn
            gr.update(visible=True),   # finalize_btn
            gr.update(visible=False)   # status_output
        )
    except Exception as e:
        return (
            gr.update(value=f"❌ Error during editing: {str(e)}"),
            gr.update(value=""),
            *[gr.update(visible=False)] * 9
        )

def edit_content():
    """Edit current content manually"""
    if STATE["current_stage"] == "edited" and STATE["edited_data"]:
        content = STATE["edited_data"]["content"]
    elif STATE["current_stage"] == "reviewed" and STATE["reviewed_data"]:
        content = STATE["reviewed_data"]["content"]
    elif STATE["current_stage"] == "rewritten" and STATE["rewritten_data"]:
        content = STATE["rewritten_data"]["content"]
    else:
        content = ""
    
    STATE["editing_content"] = True
    return content

def edit_feedback():
    """Edit reviewer feedback"""
    if STATE["reviewed_data"] is None:
        latest = get_latest_version("chapter1", "reviewed")
        if latest == 0:
            return "❌ No reviewed data found!"
        reviewed_data = fetch_chapter_by_version(f"chapter1_ver{latest}", "reviewed")
        STATE["reviewed_data"] = reviewed_data
    
    STATE["editing_feedback"] = True
    return STATE["reviewed_data"]["metadata"]["reviewer_feedback"]

def save_edited_content(edited_content):
    """Save manually edited content"""
    STATE["editing_content"] = False
    
    try:
        if STATE["current_stage"] == "edited":
            STATE["edited_data"]["content"] = edited_content
            save_data = {
                "book_title": STATE["edited_data"]["metadata"]["book_title"],
                "author": STATE["edited_data"]["metadata"]["author"],
                "chapter_info": STATE["edited_data"]["metadata"]["chapter_info"],
                "chapter_title": STATE["edited_data"]["metadata"]["chapter_title"],
                "content": edited_content,
                "source_url": STATE["edited_data"]["metadata"]["source_url"],
                "reviewer_feedback": STATE["edited_data"]["metadata"]["reviewer_feedback"]
            }
            save_chapter_auto_version(save_data, "chapter1", "human_edited")
            return (
                format_chapter_markdown(STATE["edited_data"]),
                STATE["edited_data"]["metadata"]["reviewer_feedback"]
            )
        elif STATE["current_stage"] == "reviewed":
            STATE["reviewed_data"]["content"] = edited_content
            save_data = {
                "book_title": STATE["reviewed_data"]["metadata"]["book_title"],
                "author": STATE["reviewed_data"]["metadata"]["author"],
                "chapter_info": STATE["reviewed_data"]["metadata"]["chapter_info"],
                "chapter_title": STATE["reviewed_data"]["metadata"]["chapter_title"],
                "content": edited_content,
                "source_url": STATE["reviewed_data"]["metadata"]["source_url"],
                "reviewer_feedback": STATE["reviewed_data"]["metadata"]["reviewer_feedback"]
            }
            save_chapter_auto_version(save_data, "chapter1", "human_edited")
            return (
                format_chapter_markdown(STATE["reviewed_data"]),
                STATE["reviewed_data"]["metadata"]["reviewer_feedback"]
            )
        elif STATE["current_stage"] == "rewritten":
            STATE["rewritten_data"]["content"] = edited_content
            save_data = {
                "book_title": STATE["rewritten_data"]["metadata"]["book_title"],
                "author": STATE["rewritten_data"]["metadata"]["author"],
                "chapter_info": STATE["rewritten_data"]["metadata"]["chapter_info"],
                "chapter_title": STATE["rewritten_data"]["metadata"]["chapter_title"],
                "content": edited_content,
                "source_url": STATE["rewritten_data"]["metadata"]["source_url"],
                "reviewer_feedback": STATE["rewritten_data"]["metadata"].get("reviewer_feedback", "")
            }
            save_chapter_auto_version(save_data, "chapter1", "human_edited")
            return (
                format_chapter_markdown(STATE["rewritten_data"]),
                ""
            )
    except Exception as e:
        return (
            f"❌ Error saving edited content: {str(e)}",
            ""
        )

def save_edited_feedback(edited_feedback):
    """Save edited feedback"""
    STATE["editing_feedback"] = False
    STATE["reviewed_data"]["metadata"]["reviewer_feedback"] = edited_feedback
    
    try:
        save_data = {
            "book_title": STATE["reviewed_data"]["metadata"]["book_title"],
            "author": STATE["reviewed_data"]["metadata"]["author"],
            "chapter_info": STATE["reviewed_data"]["metadata"]["chapter_info"],
            "chapter_title": STATE["reviewed_data"]["metadata"]["chapter_title"],
            "content": STATE["reviewed_data"]["content"],
            "source_url": STATE["reviewed_data"]["metadata"]["source_url"],
            "reviewer_feedback": edited_feedback
        }
        save_chapter_auto_version(save_data, "chapter1", "human_reviewed")
        
        return (
            format_chapter_markdown(STATE["reviewed_data"]),
            edited_feedback
        )
    except Exception as e:
        return (
            f"❌ Error saving edited feedback: {str(e)}",
            edited_feedback
        )

def finalize_chapter():
    """Save final version"""
    try:
        if STATE["current_stage"] == "edited" and STATE["edited_data"]:
            data_to_save = STATE["edited_data"]
        elif STATE["current_stage"] == "reviewed" and STATE["reviewed_data"]:
            data_to_save = STATE["reviewed_data"]
        elif STATE["current_stage"] == "rewritten" and STATE["rewritten_data"]:
            data_to_save = STATE["rewritten_data"]
        else:
            return "❌ No data found to finalize!"

        save_data = {
            "book_title": data_to_save["metadata"]["book_title"],
            "author": data_to_save["metadata"]["author"],
            "chapter_info": data_to_save["metadata"]["chapter_info"],
            "chapter_title": data_to_save["metadata"]["chapter_title"],
            "content": data_to_save["content"],
            "source_url": data_to_save["metadata"]["source_url"],
            "reviewer_feedback": data_to_save["metadata"].get("reviewer_feedback", "")
        }
        save_chapter_auto_version(save_data, "chapter1", "final")
        return "🎉 Final version saved successfully! Ready for publication."
    except Exception as e:
        return f"❌ Error finalizing chapter: {str(e)}"

# Create the Gradio interface
with gr.Blocks(title="Chapter Processing Pipeline") as ui:
    gr.Markdown("# 📚 Chapter Processing Pipeline")
    
    with gr.Row():
        url_input = gr.Textbox(label="Enter Wikisource URL", placeholder="https://en.wikisource.org/wiki/...")
        fetch_btn = gr.Button("🔍 Fetch Chapter", variant="primary")

    with gr.Row():
        with gr.Column(scale=3):
            main_window = gr.Markdown(label="Chapter Content", value="Upload a chapter to begin...")
            feedback_output = gr.Textbox(label="Reviewer Feedback", visible=False, lines=5)
        
        with gr.Column(scale=2, visible=False) as edit_panel:
            gr.Markdown("### ✏️ Edit Mode")
            edit_box = gr.Textbox(label="Edit Content/Feedback", lines=15)
            with gr.Row():
                save_edit_btn = gr.Button("💾 Save Changes", variant="primary")
                cancel_edit_btn = gr.Button("❌ Cancel")

    # Special instructions panel
    with gr.Row(visible=False) as special_panel:
        with gr.Column():
            gr.Markdown("### 🎯 Special Instructions")
            special_instr_box = gr.Textbox(label="Enter your rewriting instructions", lines=3, 
                                         placeholder="e.g., 'Emphasize atmospheric descriptions', 'Make dialogue more formal', etc.")
            special_instr_btn = gr.Button("🔄 Rewrite with Instructions", variant="primary")

    # Control buttons
    with gr.Row():
        rewrite_btn = gr.Button("🔄 Rewrite", visible=False)
        rewrite_special_btn = gr.Button("🎯 Rewrite with Special Instructions", visible=False)
        rewrite_again_btn = gr.Button("🔄 Rewrite Again", visible=False)
    
    with gr.Row():
        reviewer_btn = gr.Button("🔍 Send to Reviewer", visible=False)
        editor_btn = gr.Button("✏️ Edit with AI", visible=False)
        edit_btn = gr.Button("📝 Edit Content", visible=False)
        edit_feedback_btn = gr.Button("📝 Edit Feedback", visible=False)
        finalize_btn = gr.Button("🎉 Finalize", visible=False, variant="primary")

    status_output = gr.Textbox(label="Status", visible=False)

    # Event handlers
    fetch_btn.click(
        fetch_chapter,
        inputs=[url_input],
        outputs=[main_window, feedback_output, rewrite_btn, rewrite_special_btn, rewrite_again_btn,
                reviewer_btn, editor_btn, edit_btn, edit_feedback_btn, finalize_btn, status_output]
    )
    
    rewrite_btn.click(
        lambda: rewrite_chapter(False),
        outputs=[main_window, feedback_output, rewrite_btn, rewrite_special_btn, rewrite_again_btn,
                reviewer_btn, editor_btn, edit_btn, edit_feedback_btn, finalize_btn, status_output]
    )
    
    rewrite_special_btn.click(
        lambda: (gr.update(visible=True), gr.update(visible=False)),
        outputs=[special_panel, edit_panel]
    )
    
    special_instr_btn.click(
        save_special_instruction,
        inputs=[special_instr_box],
        outputs=[main_window, feedback_output, rewrite_btn, rewrite_special_btn, rewrite_again_btn,
                reviewer_btn, editor_btn, edit_btn, edit_feedback_btn, finalize_btn, status_output]
    ).then(
        lambda: gr.update(visible=False),
        outputs=[special_panel]
    )
    
    rewrite_again_btn.click(
        rewrite_again,
        outputs=[main_window, feedback_output, rewrite_btn, rewrite_special_btn, rewrite_again_btn,
                reviewer_btn, editor_btn, edit_btn, edit_feedback_btn, finalize_btn, status_output]
    )
    
    reviewer_btn.click(
        review_chapter,
        outputs=[main_window, feedback_output, rewrite_btn, rewrite_special_btn, rewrite_again_btn,
                reviewer_btn, editor_btn, edit_btn, edit_feedback_btn, finalize_btn, status_output]
    ).then(
        lambda: gr.update(visible=True),
        outputs=[feedback_output]
    )
    
    editor_btn.click(
        edit_with_feedback,
        outputs=[main_window, feedback_output, rewrite_btn, rewrite_special_btn, rewrite_again_btn,
                reviewer_btn, editor_btn, edit_btn, edit_feedback_btn, finalize_btn, status_output]
    )
    
    edit_btn.click(
        lambda: (gr.update(visible=True), gr.update(visible=False)),
        outputs=[edit_panel, special_panel]
    ).then(
        edit_content,
        outputs=[edit_box]
    )
    
    edit_feedback_btn.click(
        lambda: (gr.update(visible=True), gr.update(visible=False)),
        outputs=[edit_panel, special_panel]
    ).then(
        edit_feedback,
        outputs=[edit_box]
    )
    
    save_edit_btn.click(
        lambda content: (
            save_edited_content(content) if STATE["editing_content"] 
            else save_edited_feedback(content)
        ),
        inputs=[edit_box],
        outputs=[main_window, feedback_output]
    ).then(
        lambda: gr.update(visible=False),
        outputs=[edit_panel]
    )
    
    cancel_edit_btn.click(
        lambda: (gr.update(visible=False), "", ""),
        outputs=[edit_panel, edit_box, status_output]
    )
    
    finalize_btn.click(
        finalize_chapter,
        outputs=[status_output]
    ).then(
        lambda: gr.update(visible=True),
        outputs=[status_output]
    )

if __name__ == "__main__":
    ui.launch(share=True, inbrowser=True)