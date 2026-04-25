import sys
import os
# Ensure the script can find all modules
sys.path.append(os.getcwd())

from agents.debt_detector import detect_concept_debt
from agents.concept_debt_ledger import ConceptDebtLedger
from agents.explanation_agent import ExplanationAgent
from pipeline.schemas import KeyIdea, Chunk, DebtEntry

def test_full_member2_integration():
    print("🚀 Starting Member 2 Integration Test...")
    
    # 1. SETUP: Initialize Ledger
    ledger = ConceptDebtLedger("data/student_test.db")
    explainer = ExplanationAgent()
    
    # 2. MISCONCEPTION CHECK: Pretend a student missed a concept
    topic = "transformers"
    # These are ideas the student failed to mention or understand
    missing_from_student = ["Self-Attention Mechanism", "Word Representations"]
    
    print("\n🔍 Step 1: Detecting Debt from missing ideas...")
    detected_debts = detect_concept_debt(topic, missing_from_student)
    
    # 3. LEDGER SAVE: Store the debt in the database
    print(f"💾 Step 2: Saving {len(detected_debts)} debts to SQLite...")
    ledger.add_debts("student_123", detected_debts)
    
    # 4. RECOVERY: Retrieve debts to "Repair" the student in the next explanation
    print("📖 Step 3: Retrieving open debts for 'student_123'...")
    open_rows = ledger.get_open_debts("student_123")
    
    # Convert DB rows back to your shared DebtEntry schema
    active_debts = [
        DebtEntry(
            prerequisite_concept=d["missing_concept"],
            severity=d["severity"],
            evidence=d["reason"]
        ) for d in open_rows
    ]
    
    # 5. EXPLANATION: See if the "Repair" section appears
    print("📝 Step 4: Generating 'Repair' Explanation...")
    query = "How do Transformers work?"
    mock_chunks = [Chunk(text="Transformers are cool.", metadata={"source":"lec.pdf"})]
    mock_ideas = [KeyIdea(name="Transformers", description="Global context model")]
    
    response = explainer.generate_explanation(query, mock_ideas, mock_chunks, active_debts)
    
    print("\n" + "="*50)
    print("FINAL INTEGRATED RESPONSE:")
    print(response)
    print("="*50)
    
    if "### 🛠️ Prerequisite Foundations" in response:
        print("\n✅ SUCCESS: Member 1 and Member 2 components are integrated!")
    else:
        print("\n❌ FAILURE: Repair section not found.")

if __name__ == "__main__":
    test_full_member2_integration()
