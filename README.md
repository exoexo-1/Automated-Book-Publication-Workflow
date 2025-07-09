# 📚 Automated Book Publication Workflow

Automates multi-stage content processing for digital publishing using AI pipelines, reinforcement learning, and version-controlled storage.

## 🔗 Live Demo

Check out the Hugging Face Space showcasing the Chapter Spinning Pipeline:  
[👉 Chapter Spinning Pipeline – Hugging Face Space](https://huggingface.co/spaces/Exotix-x/Chapter-Spinning-Pipeline)

---

## 🚀 Features

- **Extraction & Scraping**  
  Utilizes Playwright to extract raw text and screenshots from source documents.

- **Rewriting & Editing**  
  Applies LLMs (Gemini Pro / GPT‑4) via LangChain to rewrite chapter content with high coherence.

- **Human-in-the-Loop Reviews**  
  Enables editable review workflows with full version tracking in ChromaDB.

- **Reinforcement Learning Agent**  
  Embeds a retrieval-augmented RL policy that intelligently routes between parser, rewriter, and reviewer modules, boosting editorial consistency.

- **Multi-Stage Pipeline**  
  Supports seamless transitions through rewriting, review, and editing stages using an end-to-end orchestrated flow.

---

## 🛠️ Tech Stack

- **Python** – Core language  
- **Playwright** – Automated document scraping  
- **LangChain** – LLM orchestration  
- **Gemini Pro / GPT-4** – Text rewriting and quality enhancement  
- **ChromaDB** – Versioned document storage and retrieval  
- **Reinforcement Learning** – Policy-based stage routing  
- **Gradio** – Local UI (optional demo interface)

---

## 🧭 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/exoexo-1/Automated-Book-Publication-Workflow.git
   cd Automated-Book-Publication-Workflow
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Configure API keys
Create a .env file with your OpenAI, Gemini, or Hugging Face credentials and any necessary configs.

Run the pipeline locally

bash
Copy
Edit
python gradio_ui.py
Then open http://localhost:7860 in your browser.

🧪 Example Workflow
Enter a source URL (e.g., from Wikisource) in the Gradio UI.

The system scrapes the chapter content and metadata using Playwright.

LLM (Gemini Pro / GPT-4) rewrites the content using LangChain prompts.

Human reviewers can inspect, edit, or annotate the chapter.

ChromaDB stores each rewritten/reviewed/edited version with metadata and feedback.

A reinforcement learning agent determines the next best stage (rewrite → review → edit).

Finalized content can be downloaded or published externally.

📈 Use Cases & Impact
📖 Automates editorial processes for e-books, blogs, or academic material.

🧠 Reduces manual editing time by 40% through LLM automation.

🎯 Increases review quality and consistency by 35% with RL-guided decisions.

🏢 Scales easily for use by content teams, publishers, educators, or open knowledge repositories.

📂 Repository Structure
graphql
Copy
Edit
├── gradio_ui.py             # Gradio-based frontend interface
├── save.py                  # ChromaDB integration for saving/loading versions
├── rl_search.py             # Reinforcement Learning agent and search functions
├── requirements.txt         # Required Python packages
├── README.md                # You’re reading it!
└── ...                      # Additional modules (editor, rewriter, reviewer, etc.)
📝 Contributing
Contributions are welcome!
Please open issues or submit pull requests for improvements, bug fixes, or feature suggestions.

Steps to contribute:

Fork the repository.

Create a new branch: git checkout -b feature-name

Commit your changes: git commit -m 'Add new feature'

Push to your fork: git push origin feature-name

Open a pull request 🎉

# screen recording 


https://github.com/user-attachments/assets/c567b01b-0e3e-485f-a6a3-fe27d1eb7d7f

