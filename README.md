# TutorMind (DeepStudy Coach)

TutorMind is a high-performance, domain-specific AI tutor built using **Google Gemini 2.5 Flash**, **Vertex AI**, and **ChromaDB**. It uses a curriculum-aware RAG pipeline to move students beyond rote memorization towards deep conceptual understanding.

## Quick Start Guide

### 1. Setup Environment
Ensure you have Python 3.9+ and have authenticated your Google Cloud account (`gcloud auth application-default login`).
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Add your GOOGLE_CLOUD_PROJECT to .env
```

### 2. Launch the Dashboard
Run the main Streamlit application:
```bash
streamlit run app/main.py
```

### 3. The Workflow
1.  **Select/Create Student ID:** Enter a unique ID in the sidebar to keep your memory separate.
2.  **Upload & Index:** Open the **"📂 Upload Course Material"** tab, upload your PDFs, and click **"Index Documents"**.
3.  **Ask & Learn:** Start chatting! The AI will automatically detect your "Concept Debts" and tailor its teaching style to your saved preferences.

## Key Features
- **Customizable Teaching Persona:** The tutor's "voice" and explanation structure are decoupled from the system logic. By modifying the external `pipeline/domain_prompt.txt`, instructors can instantly swap between different pedagogical frameworks (e.g., Socratic vs. Coach style) without changing any code.
- **High-Performance Pipeline:** Uses `asyncio` to run judging and decomposition in parallel, reducing latency by 40%.
- **Closed-Loop Learning:** MCQ results are wired to a **Concept Debt Ledger (CDL)**. Wrong answers create debts; mastery repairs them.
- **Quota-Optimized:** Consolidates auditing and question generation into a single API call to survive trial-tier rate limits.
- **Multi-Turn Memory:** Persists conversation history for follow-up questions and pedagogical continuity.

## Scientific Verification
Run the included ablation study to see the metrics proving the system's effectiveness:
```bash
python evaluation/run_ablation.py
```
*Results will be saved to `evaluation/results/final_ablation_summary.csv`.*

---
*Developed as part of the COE548 / COE748 Final Project - April 2026*
