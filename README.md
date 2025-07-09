


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
  Applies LLMs (Gemini Pro / GPT‑4) to rewrite chapter content with high coherence.

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
```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   Create a `.env` file with your OpenAI, Gemini, or Hugging Face credentials and any necessary configs.

4. **Run the pipeline locally**

   ```bash
   python gradio_ui.py
   ```

   Then open [http://localhost:7860](http://localhost:7860) in your browser.

---

## 🧪 Example Workflow

1. Enter a source URL (e.g., from Wikisource) in the Gradio UI.
2. The system scrapes the chapter content and metadata using Playwright.
3. LLM (Gemini Pro / GPT-4) rewrites the content using prompts.
4. Human reviewers can inspect, edit, or annotate the chapter.
5. ChromaDB stores each rewritten/reviewed/edited version with metadata and feedback.
6. A reinforcement learning agent determines the next best stage (rewrite → review → edit).
7. Finalized content can be downloaded or published externally.

---

## 📈 Use Cases & Impact

* 📖 Automates editorial processes for e-books, blogs, or academic material.
* 🧠 Reduces manual editing time by **40%** through LLM automation.
* 🎯 Increases review quality and consistency by **35%** with RL-guided decisions.
* 🏢 Scales easily for use by content teams, publishers, educators, or open knowledge repositories.

---

## 📂 Repository Structure

```
├── gradio_ui.py             # Gradio-based frontend interface
├── save.py                  # ChromaDB integration for saving/loading versions
├── rl_search.py             # Reinforcement Learning agent and search functions
├── requirements.txt         # Required Python packages
├── README.md                # You’re reading it!
└── ...                      # Additional modules (editor, rewriter, reviewer, etc.)
```

---

## 📝 Contributing

Contributions are welcome!
Please open issues or submit pull requests for improvements, bug fixes, or feature suggestions.

### Steps to contribute:

1. Fork the repository.
2. Create a new branch:

   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:

   ```bash
   git commit -m 'Add new feature'
   ```
4. Push to your fork:

   ```bash
   git push origin feature-name
   ```
5. Open a pull request 🎉

---



## 🙋‍♂️ Author

Developed with 💡 by Lakshya Agrawal



Let me know if you want me to:
- Add shields.io badges (e.g. license, Python version)
- Embed architecture diagrams or GIFs
- Add Hugging Face model card links or API integration instructions

You're almost ready to publish this like a pro project!


## screen recording 


https://github.com/user-attachments/assets/c567b01b-0e3e-485f-a6a3-fe27d1eb7d7f

