# DeepStudy Coach (TutorMind)

DeepStudy Coach is a domain-specific, teaching-aware AI tutor built using **LangChain**, Google Gemini 2.5 Flash, and RAG (Retrieval-Augmented Generation). It is designed to help students achieve deep conceptual understanding rather than just memorizing answers.

## 🚀 Key Features
- **Teaching-Aware Retrieval (TARJ):** Filters course material for pedagogical quality, not just keyword relevance.
- **Concept Debt Ledger (CDL):** Tracks missing prerequisite knowledge across sessions and provides proactive "repairs."
- **Coverage Verification (ECV):** Ensures every key sub-concept is addressed before delivering an answer.
- **Structured Explanations:** Automatically includes analogies, intuition-first bridges, and self-check MCQs.

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9 or higher
- A Google Gemini API Key (get one at [AI Studio](https://aistudio.google.com/))

### Installation
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd LLMs_Project
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Copy the example environment file and add your Gemini API Key:
   ```bash
   cp .env.example .env
   # Open .env and set GOOGLE_API_KEY=your_actual_key
   ```

## 💻 How to Run
To start the AI Tutor interface:
```bash
streamlit run app/main.py
```

## 📁 Project Structure
- `app/`: Streamlit UI entry point and configurations.
- `agents/`: Specialized AI agents (Judge, Decomposer, Explainer, Verifier).
- `pipeline/`: The core `teaching_pipeline` logic.
- `memory/`: Persistence layers (Concept Debt, Weak Topics, Session History).
- `tools/`: Utility modules for document loading, chunking, and LLM communication.
- `data/`: Local storage for the vector database and student SQLite DB.
- `finetuning/`: Domain-specific Q&A examples for pedagogical calibration.

## 🧪 Evaluation
The project includes an evaluation suite to measure the effectiveness of the teaching-aware components via an ablation study:
```bash
python evaluation/run_ablation.py
```

---
*Developed as part of the COE548 / COE748 Final Project - April 2026*
