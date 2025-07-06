import gradio as gr
from ScreenShot_scrapper import extract_chapter_info
from save import (
    save_chapter_auto_version, get_latest_version, fetch_chapter_by_version,
    format_chapter_markdown, get_next_version, intelligent_search,
    search_by_stage_progression, provide_search_feedback, get_search_analytics,
    save_rl_model, select_policy_stage, update_policy_stage as update_policy,
    get_policy_stats, save_policy_model
)
from Rewriter import rewriter
from Reviewer import reviwer
from editor import editor
import traceback

# Global state management
STATE = {
    "current_stage": "init",
    "raw_data": None,
    "rewritten_data": None,
    "reviewed_data": None,
    "edited_data": None,
    "special_instruction": "None",
    "editing_content": False,
    "editing_feedback": False,
    "last_policy_suggestion": None,  
    "policy_feedback": []
}

def reset_state():
    """Reset the global state"""
    global STATE
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

def safe_execute(func, *args, **kwargs):
    """Safely execute functions with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_msg = f"❌ Error in {func.__name__}: {str(e)}"
        print(f"Error details: {traceback.format_exc()}")
        return error_msg

def fetch_chapter(url):
    """Fetch chapter from Wikisource URL with RL search integration"""
    if not url or not url.strip():
        return create_error_response("❌ Please enter a URL!")
    
    if not url.startswith("https://en.wikisource.org/wiki"):
        return create_error_response("❌ Invalid URL! Please use a valid Wikisource URL.")
    

    try:
        reset_state()
        data = extract_chapter_info(url)
        
        if not data or not data.get("content"):
            return create_error_response("❌ Failed to extract chapter content!")
        
        # Save raw data
        save_chapter_auto_version({
            **data,
            "reviewer_feedback": ""
        }, base_id="chapter1", stage="raw")

        # Get policy suggestion with context
        next_action = select_policy_stage({
            "current_stage": "raw",
            "url": url,
            "previous_actions": []
        })
        STATE["last_policy_suggestion"] = next_action
        print(f"🤖 Policy suggests next stage: {next_action}")

        # Update state
        STATE["raw_data"] = {
            "content": data["content"],
            "metadata": {
                **data,
                "version": get_latest_version("chapter1", "raw"),
                "stage": "raw",
                "versioned_id": f"chapter1_ver{get_latest_version('chapter1', 'raw')}",
                "reviewer_feedback": ""
            }
        }
        STATE["current_stage"] = "raw"

        suggestion_text = f"🤖 Suggested Next Step: {next_action.capitalize()}"
        button_states = get_button_states_for_action(next_action)
        
        return (
            format_chapter_markdown(STATE["raw_data"]),
            gr.update(value=suggestion_text),
            *button_states
        )
        
    except Exception as e:
        return create_error_response(f"❌ Error fetching chapter: {str(e)}")
    
def get_button_states_for_action(action):
    """Return button visibility states based on suggested action"""
    base_states = [
        gr.update(visible=True),   # rewrite_btn
        gr.update(visible=True),   # rewrite_special_btn
        gr.update(visible=False),  # rewrite_again_btn
        gr.update(visible=False),  # reviewer_btn
        gr.update(visible=False),  # editor_btn
        gr.update(visible=False),  # edit_btn
        gr.update(visible=False),  # edit_feedback_btn
        gr.update(visible=False),  # finalize_btn
        gr.update(visible=False),  # status_output
        gr.update(visible=False)   # special_panel
    ]
    
    if action == "rewritten":
        base_states[0] = gr.update(visible=True, variant="primary")  # Highlight rewrite button
    elif action == "edited":
        base_states[3] = gr.update(visible=True, variant="primary")  # Highlight reviewer button
    
    return base_states

def create_error_response(error_msg):
    """Create consistent error response"""
    return (
        gr.update(value=error_msg),
        gr.update(value=""),
        *[gr.update(visible=False)] * 9,
        gr.update(visible=False)  # special_panel
    )

def smart_content_search(query):
    """Search content using RL algorithm"""
    if not query or not query.strip():
        return "Please enter a search query"
    
    try:
        results = search_by_stage_progression(query)
        
        if not results:
            return "No results found"
        
        formatted_results = "## 🔍 Smart Search Results\n\n"
        for i, result in enumerate(results[:3], 1):
            metadata = result.get('metadata', {})
            relevance = result.get('relevance_score', 0)
            
            formatted_results += f"### Result {i} (Relevance: {relevance:.2f})\n"
            formatted_results += f"**Title:** {metadata.get('chapter_title', 'N/A')}\n"
            formatted_results += f"**Stage:** {metadata.get('stage', 'N/A')} | **Version:** {metadata.get('version', 'N/A')}\n"
            
            content_preview = result.get('content', '')[:200]
            formatted_results += f"**Content Preview:** {content_preview}...\n\n"
            formatted_results += "---\n\n"
        
        provide_search_feedback(clicked_result=True, satisfaction_score=4)
        return formatted_results
        
    except Exception as e:
        return f"❌ Search error: {str(e)}"

def show_analytics():
    try:
        stats = get_search_analytics()
        policy_info = get_policy_stats()
        
        analytics = "## 📊 System Analytics\n\n"
        
        # Policy Insights
        analytics += "### 🤖 Policy Insights\n"
        analytics += f"**Last Suggestion:** {STATE.get('last_policy_suggestion', 'None')}\n"
        analytics += "**Action Preferences:**\n"
        for action, pref in policy_info["preferences"].items():
            prob = policy_info["probabilities"][action]
            analytics += f"- {action.capitalize()}: Preference={pref:.2f}, Probability={prob:.2f}\n"
        
        # Search Analytics (if available)
        if stats:
            analytics += "\n### 🔍 Search Analytics\n"
            analytics += f"**Total Searches:** {stats.get('total_searches', 0)}\n"
            analytics += f"**Average Reward:** {stats.get('average_reward', 0):.3f}\n"
            if 'action_distribution' in stats:
                analytics += "**Action Usage:**\n"
                for action, count in stats['action_distribution'].items():
                    analytics += f"- {action}: {count}\n"
        
        return analytics
    except Exception as e:
        return f"❌ Analytics error: {str(e)}"
def rewrite_chapter(use_special):
    """Handle chapter rewriting"""
    if STATE["raw_data"] is None:
        latest = get_latest_version("chapter1", "raw")
        if latest == 0:
            return create_error_response("❌ No raw data found!")
        STATE["raw_data"] = fetch_chapter_by_version(f"chapter1_ver{latest}", "raw")

    if use_special:
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
            gr.update(visible=False),  # status_output
            gr.update(visible=True)    # special_panel
        )
    else:
        try:
            result = rewriter(STATE["raw_data"], "None")
            rewritten_content = {
                "content": result.get("content", result) if isinstance(result, dict) else result,
                "metadata": {**STATE["raw_data"]["metadata"], "reviewer_feedback": ""}
            }
            
            if isinstance(result, dict):
                rewritten_content["metadata"].update(result)
            
            STATE["rewritten_data"] = rewritten_content
            STATE["current_stage"] = "rewritten"
            
            save_chapter_auto_version({
                **rewritten_content["metadata"], 
                "content": rewritten_content["content"]
            }, "chapter1", "rewritten")
            reward = 1 if STATE["last_policy_suggestion"] == "rewritten" else 0.5
            update_policy("rewritten", reward)

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
                gr.update(visible=False),  # status_output
                gr.update(visible=False)   # special_panel
            )
        except Exception as e:
            update_policy("rewritten", -0.5)
            return create_error_response(f"❌ Error during rewriting: {str(e)}")

def save_special_instruction(instr):
    """Save special instruction and rewrite"""
    STATE["special_instruction"] = instr or "None"
    
    try:
        result = rewriter(STATE["raw_data"], instr or "None")
        rewritten_content = {
            "content": result.get("content", result) if isinstance(result, dict) else result,
            "metadata": {**STATE["raw_data"]["metadata"], "reviewer_feedback": ""}
        }
        
        if isinstance(result, dict):
            rewritten_content["metadata"].update(result)
        
        STATE["rewritten_data"] = rewritten_content
        STATE["current_stage"] = "rewritten"
        
        save_chapter_auto_version({
            **rewritten_content["metadata"], 
            "content": rewritten_content["content"]
        }, "chapter1", "rewritten")

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
            gr.update(visible=False),  # status_output
            gr.update(visible=False)   # special_panel
        )
    except Exception as e:
        return create_error_response(f"❌ Error during special rewrite: {str(e)}")

def rewrite_again():
    """Reset to raw stage for rewriting"""
    if STATE["raw_data"] is None:
        latest = get_latest_version("chapter1", "raw")
        if latest == 0:
            return create_error_response("❌ No raw data found!")
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
        gr.update(visible=False),  # status_output
        gr.update(visible=False)   # special_panel
    )

def review_chapter():
    """Handle review stage"""
    try:
        # Get raw data
        latest_raw = get_latest_version("chapter1", "raw")
        if latest_raw == 0:
            return create_error_response("❌ No raw data found!")
        
        raw_data = fetch_chapter_by_version(f"chapter1_ver{latest_raw}", "raw")
        if not STATE["raw_data"]:
            STATE["raw_data"] = raw_data

        # Determine what to review
        data_to_review = None
        
        if STATE["current_stage"] == "edited" and STATE["edited_data"]:
            data_to_review = STATE["edited_data"]
        elif STATE["current_stage"] == "rewritten" and STATE["rewritten_data"]:
            data_to_review = STATE["rewritten_data"]
        else:
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
                        break
            
            if not latest_data:
                return create_error_response("❌ No rewritten/edited data found to review!")
            
            data_to_review = latest_data

        # Generate feedback
        feedback = reviwer(raw_data, data_to_review)
        
        # Create reviewed data
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
                "reviewed_from_stage": data_to_review["metadata"].get("stage", "unknown")
            }
        }
        STATE["current_stage"] = "reviewed"
        
        # Save reviewed version
        save_chapter_auto_version({
            "book_title": STATE["reviewed_data"]["metadata"]["book_title"],
            "author": STATE["reviewed_data"]["metadata"]["author"],
            "chapter_info": STATE["reviewed_data"]["metadata"]["chapter_info"],
            "chapter_title": STATE["reviewed_data"]["metadata"]["chapter_title"],
            "content": STATE["reviewed_data"]["content"],
            "source_url": STATE["reviewed_data"]["metadata"]["source_url"],
            "reviewer_feedback": feedback
        }, base_id="chapter1", stage="reviewed")
        reward = 1 if STATE["last_policy_suggestion"] == "edited" else 0.5
        update_policy("edited", reward)
        
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
            gr.update(visible=False),  # status_output
        )
    except Exception as e:
        update_policy("edited", -0.5)
        return create_error_response(f"❌ Error during review: {str(e)}")

def edit_with_feedback():
    """Perform AI editing based on feedback"""
    try:
        # Get raw data
        latest_raw = get_latest_version("chapter1", "raw")
        if latest_raw == 0:
            return create_error_response("❌ No raw data found!")
        
        raw_data = fetch_chapter_by_version(f"chapter1_ver{latest_raw}", "raw")
        if not STATE["raw_data"]:
            STATE["raw_data"] = raw_data
        
        # Get reviewed data
        if STATE["reviewed_data"] is None:
            latest_reviewed = get_latest_version("chapter1", "reviewed")
            if latest_reviewed == 0:
                return create_error_response("❌ No reviewed data found!")
            reviewed_data = fetch_chapter_by_version(f"chapter1_ver{latest_reviewed}", "reviewed")
            STATE["reviewed_data"] = reviewed_data

        # Edit content
        edited_content = editor(raw_data, STATE["reviewed_data"])
        
        # Create edited data
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
        
        # Save edited version
        save_chapter_auto_version({
            "book_title": STATE["edited_data"]["metadata"]["book_title"],
            "author": STATE["edited_data"]["metadata"]["author"],
            "chapter_info": STATE["edited_data"]["metadata"]["chapter_info"],
            "chapter_title": STATE["edited_data"]["metadata"]["chapter_title"],
            "content": edited_content,
            "source_url": STATE["edited_data"]["metadata"]["source_url"],
            "reviewer_feedback": STATE["edited_data"]["metadata"]["reviewer_feedback"]
        }, base_id="chapter1", stage="edited")
        
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
            gr.update(visible=False),  # status_output
        )
    except Exception as e:
        return create_error_response(f"❌ Error during editing: {str(e)}")

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
    return (
        content,
        gr.update(interactive=False),  # All buttons disabled during editing
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False)
    )

def edit_feedback():
    """Edit reviewer feedback"""
    if STATE["reviewed_data"] is None:
        latest = get_latest_version("chapter1", "reviewed")
        if latest == 0:
            return ("❌ No reviewed data found!",) + tuple(gr.update() for _ in range(8))
        reviewed_data = fetch_chapter_by_version(f"chapter1_ver{latest}", "reviewed")
        STATE["reviewed_data"] = reviewed_data
    
    STATE["editing_feedback"] = True
    return (
        STATE["reviewed_data"]["metadata"]["reviewer_feedback"],
        gr.update(interactive=False),  # All buttons disabled during editing
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False)
    )

def save_edited_content(edited_content):
    """Save manually edited content"""
    STATE["editing_content"] = False
    
    try:
        if STATE["current_stage"] == "edited" and STATE["edited_data"]:
            STATE["edited_data"]["content"] = edited_content
            save_data = {
                **STATE["edited_data"]["metadata"],
                "content": edited_content
            }
            save_chapter_auto_version(save_data, "chapter1", "human_edited")
            return create_save_response(STATE["edited_data"])
            
        elif STATE["current_stage"] == "reviewed" and STATE["reviewed_data"]:
            STATE["reviewed_data"]["content"] = edited_content
            save_data = {
                **STATE["reviewed_data"]["metadata"],
                "content": edited_content
            }
            save_chapter_auto_version(save_data, "chapter1", "human_edited")
            return create_save_response(STATE["reviewed_data"])
            
        elif STATE["current_stage"] == "rewritten" and STATE["rewritten_data"]:
            STATE["rewritten_data"]["content"] = edited_content
            save_data = {
                **STATE["rewritten_data"]["metadata"],
                "content": edited_content
            }
            save_chapter_auto_version(save_data, "chapter1", "human_edited")
            return create_save_response(STATE["rewritten_data"])
            
    except Exception as e:
        return create_error_save_response(f"❌ Error saving edited content: {str(e)}")

def create_save_response(data):
    """Create response for successful save"""
    return (
        format_chapter_markdown(data),
        data["metadata"].get("reviewer_feedback", ""),
        gr.update(interactive=True),  # Re-enable all buttons
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True)
    )

def create_error_save_response(error_msg):
    """Create error response for save operations"""
    return (
        error_msg,
        "",
        gr.update(interactive=True),  # Re-enable all buttons
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True)
    )

def save_edited_feedback(edited_feedback):
    """Save edited feedback"""
    STATE["editing_feedback"] = False
    STATE["reviewed_data"]["metadata"]["reviewer_feedback"] = edited_feedback
    
    try:
        save_data = {
            **STATE["reviewed_data"]["metadata"],
            "content": STATE["reviewed_data"]["content"],
            "reviewer_feedback": edited_feedback
        }
        save_chapter_auto_version(save_data, "chapter1", "human_reviewed")
        
        return create_save_response(STATE["reviewed_data"])
    except Exception as e:
        return create_error_save_response(f"❌ Error saving edited feedback: {str(e)}")

def cancel_edit():
    """Cancel editing and re-enable buttons"""
    STATE["editing_content"] = False
    STATE["editing_feedback"] = False
    
    return (
        gr.update(visible=False),     # edit_panel
        "",                          # edit_box
        "",                          # status_output
        gr.update(interactive=True),  # Re-enable all buttons
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True)
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
            **data_to_save["metadata"],
            "content": data_to_save["content"]
        }
        save_chapter_auto_version(save_data, "chapter1", "final")
        return "🎉 Final version saved successfully! Ready for publication."
    except Exception as e:
        return f"❌ Error finalizing chapter: {str(e)}"

def save_model():
    """Save the RL model"""
    try:
        save_rl_model()
        return "✅ RL model saved successfully!"
    except Exception as e:
        return f"❌ Error saving model: {str(e)}"

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
    
    with gr.Tab("🤖 Smart Search"):
        with gr.Row():
            search_input = gr.Textbox(label="Search Query", placeholder="Enter search terms...")
            search_btn = gr.Button("🔍 Smart Search", variant="primary")
        
        search_results = gr.Markdown(label="Search Results", value="Enter a query to search...")
        
        with gr.Row():
            analytics_btn = gr.Button("📊 Show Analytics")
            save_model_btn = gr.Button("💾 Save RL Model")
        
        analytics_output = gr.Markdown(label="Analytics", visible=False)
    

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
        outputs=[edit_box, rewrite_btn, rewrite_special_btn, rewrite_again_btn,
                reviewer_btn, editor_btn, edit_btn, edit_feedback_btn, finalize_btn]
    )
    
    edit_feedback_btn.click(
        lambda: (gr.update(visible=True), gr.update(visible=False)),
        outputs=[edit_panel, special_panel]
    ).then(
        edit_feedback,
        outputs=[edit_box, rewrite_btn, rewrite_special_btn, rewrite_again_btn,
                reviewer_btn, editor_btn, edit_btn, edit_feedback_btn, finalize_btn]
    )
    
    save_edit_btn.click(
        lambda content: (
            save_edited_content(content) if STATE["editing_content"] 
            else save_edited_feedback(content)
        ),
        inputs=[edit_box],
        outputs=[main_window, feedback_output, rewrite_btn, rewrite_special_btn, rewrite_again_btn,
                reviewer_btn, editor_btn, edit_btn, edit_feedback_btn, finalize_btn]
    ).then(
        lambda: gr.update(visible=False),
        outputs=[edit_panel]
    )
    
    cancel_edit_btn.click(
        cancel_edit,
        outputs=[edit_panel, edit_box, status_output, rewrite_btn, rewrite_special_btn, rewrite_again_btn,
                reviewer_btn, editor_btn, edit_btn, edit_feedback_btn, finalize_btn]
    )
    
    finalize_btn.click(
        finalize_chapter,
        outputs=[status_output]
    ).then(
        lambda: gr.update(visible=True),
        outputs=[status_output]
    )


    search_btn.click(
        smart_content_search,
        inputs=[search_input],
        outputs=[search_results]
    )
    
    analytics_btn.click(
        show_analytics,
        outputs=[analytics_output]
    ).then(
        lambda: gr.update(visible=True),
        outputs=[analytics_output]
    )
    
    save_model_btn.click(
        save_model,
        outputs=[analytics_output]  # Show save status in analytics output
    ).then(
        lambda: gr.update(visible=True),
        outputs=[analytics_output]
    )

if __name__ == "__main__":
    ui.launch(share=True, inbrowser=True)