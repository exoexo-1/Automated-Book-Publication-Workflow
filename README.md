# Developing - Automated-Book-Publication-Workflow


*Objective:* Create a system to fetch content from a web URL, apply an AI-driven "spin" to chapters, allow multiple human-in-the-loop iterations. 

Key Capabilities:

1.Scraping & Screenshots: Fetch content and save screenshots from https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1.
2.AI Writing & Review: Use LLMs (e.g., Gemini) for chapter "spinning" by an AI Writer and refinement by an AI Reviewer.
3.Human-in-the-Loop: Facilitate multiple iterations with human input for writers, reviewers, and editors before finalization.
4.Agentic API: Ensure seamless content flow between AI agents.
5.Versioning & Consistency: Save final versions and enable consistent retrieval of published content using ChromaDB for storage and a RL search algorithm for intelligent retrieval.
Core Tools:

Python: Primary development language.
Playwright: For web scraping and screenshots.
LLM: For AI writing, reviewing, and editing.
ChromaDB: For content versioning and search.
RL Search Algorithm: For consistent data retrieval.


# screen recording 


https://github.com/user-attachments/assets/c567b01b-0e3e-485f-a6a3-fe27d1eb7d7f

