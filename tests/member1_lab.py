from agents.decomposer import Decomposer
from agents.retrieval_judge import RetrievalJudge
from pipeline.schemas import Chunk

def run_member1_lab():
    decomposer = Decomposer()
    judge = RetrievalJudge(threshold=6.5) # We can tune this
    
    # --- TEST 1: DECOMPOSER ---
    topic = "Transformers and LLM Scaling Laws"
    print(f"--- STEP 1: Decomposing '{topic}' ---")
    decomposer = Decomposer()
    judge = RetrievalJudge(threshold=5.0) # Matches requirements.md

    # --- TEST 1: DECOMPOSER ---
    ...
    # --- TEST 2: RETRIEVAL JUDGE (TARJ) ---
    print(f"\n--- STEP 2: Judging Mock Chunks ---")
    mock_chunks = [
        Chunk(
            text="The Self-Attention mechanism is like a spotlight in a crowded room. Instead of listening to everyone equally (like an RNN), the model focuses its attention on the specific words that help clarify the meaning of the current word. For example, in the sentence 'The bank of the river', the word 'river' helps the model focus on the geographical meaning of 'bank'.",
            metadata={"source": "expert_tutorial.pdf"}
        ),
        Chunk(
            text="x = [1, 2, 3]; y = [4, 5, 6]; result = x @ y.T",
            metadata={"source": "code_snippet.py"}
        ),
        Chunk(
            text="Scaling laws are observed in LLMs. They show that loss decreases as N (parameters), D (dataset size), and C (compute) increase.",
            metadata={"source": "bare_facts.pdf"}
        )
    ]

    scored_chunks = judge.score_chunks(topic, mock_chunks)
    
    print("\n✅ TARJ Results (High score = kept):")
    for c in scored_chunks:
        print(f"⭐ Score: {c.pedagogical_score:.1f} | Content: {c.text[:60]}...")

if __name__ == "__main__":
    run_member1_lab()
