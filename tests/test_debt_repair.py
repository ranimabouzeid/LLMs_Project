from agents.explanation_agent import ExplanationAgent
from pipeline.schemas import KeyIdea, Chunk, DebtEntry

def test_debt_repair():
    agent = ExplanationAgent()
    
    query = "How do Transformers use Attention?"
    key_ideas = [KeyIdea(name="Self-Attention", description="Weighing importance of input tokens.")]
    chunks = [Chunk(text="Attention mechanisms allow models to focus.", metadata={"source": "lec.pdf"})]
    
    # MOCK DEBT: Pretend the student doesn't understand 'Neural Networks'
    mock_debts = [
        DebtEntry(prerequisite_concept="Neural Network Fundamentals", severity=5, evidence="Student failed MCQ on weights.")
    ]
    
    print("⏳ Testing Explanation with active Concept Debt...")
    response = agent.generate_explanation(query, key_ideas, chunks, mock_debts)
    
    print("\n" + "="*50)
    print("RESULT:")
    print(response)
    print("="*50)
    
    if "Prerequisite Foundations" in response:
        print("\n✅ SUCCESS: The agent detected the debt and added a repair section!")
    else:
        print("\n❌ FAILURE: The agent ignored the debt.")

if __name__ == "__main__":
    test_debt_repair()
