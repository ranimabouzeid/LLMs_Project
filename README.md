# DeepStudy Coach (TutorMind)

DeepStudy Coach is a domain-specific, teaching-aware AI tutor built using **Google Gemini 2.5 Flash**, **Vertex AI**, and **ChromaDB**. It is designed to move students beyond rote memorization towards deep conceptual understanding via a curriculum-aware RAG pipeline.

## 🚀 Key Features (Implemented)
- **Resilient AI Client:** Custom LLM client with automatic 429 (Rate Limit) retries and 30s connection timeouts.
- **Teaching-Aware Retrieval (TARJ):** Batched pedagogical scoring that filters source material for teaching depth.
- **Interactive Multi-Turn Chat:** Full conversation history persistence allowing for natural follow-up questions.
- **Closed-Loop Assessment:** Interactive MCQs where wrong answers automatically trigger new "Concept Debts" for future repair.
- **Instant Short-Answer Grading:** Fast, direct AI evaluation for challenge questions to build student confidence.
- **Semantic Coverage Verification (ECV):** Post-generation AI auditor that ensures every key concept from the syllabus is addressed.
- **Concept Debt Ledger (CDL):** Persistent SQLite tracking of missing prerequisite knowledge with proactive "repair" explanations.

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- Google Cloud Project with **Vertex AI API** enabled.
- Google Cloud SDK (authenticated via `gcloud auth application-default login`).

### Installation
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd LLMs_Project
   ```
2. **Setup Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

## 💻 How to Run

### 1. Index Course Materials
Place your PDFs in `data/uploads/` and run the UI or the bulk indexer:
```bash
python scripts/index_documents.py
```

### 2. Start the Dashboard
Launch the interactive learning environment:
```bash
streamlit run app/main.py
```

### 3. Check Student Memory
Inspect the SQLite database to see session history and concept debt:
```bash
python scripts/check_db.py
```

## 📁 Project Structure
- `agents/`: AI agents for judging, decomposing, and auditing explanations.
- `pipeline/`: The orchestrator (`teaching_pipeline.py`) and master schemas.
- `memory/`: Persistence engine including the `MemoryManager` and SQLite logic.
- `tools/`: Resilient LLM client and document processing tools.
- `ui/`: Streamlit components for chat, uploads, and memory visualization.

---
*Developed as part of the COE548 / COE748 Final Project - April 2026*
