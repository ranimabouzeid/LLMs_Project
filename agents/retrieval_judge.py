from typing import List
from tools.llm_client import llm_client
from pipeline.schemas import Chunk

class RetrievalJudge:
    """
    TARJ: Teaching-Aware Retrieval Judge.
    Stable sequential version with progress tracking.
    """
    def __init__(self, threshold: float = 5.0):
        self.threshold = threshold
        self.system_prompt = """
        You are a Pedagogical Quality Assessor. Score the text chunk 0-10 on "Teaching Value."
        Criteria: Explanatory Depth, Clarity, Examples.
        Return ONLY JSON: {"score": float}
        """

    def score_chunks(self, query: str, chunks: List[Chunk]) -> List[Chunk]:
        """
        Scores chunks one by one to ensure stability.
        """
        approved_chunks = []
        
        print(f"⏳ Starting TARJ Judging for {len(chunks)} chunks...")

        for i, chunk in enumerate(chunks, 1):
            print(f"  [{i}/{len(chunks)}] Scoring chunk: {chunk.text[:40]}...")
            
            user_msg = f"Query: {query}\n\nChunk Content: {chunk.text}"
            
            try:
                response = llm_client.chat(
                    system_prompt=self.system_prompt,
                    user_message=user_msg,
                    json_mode=True
                )
                score = response.get("score", 0.0)
                chunk.pedagogical_score = score
                print(f"  ✅ Result: {score}/10.0")
            except Exception as e:
                print(f"  ❌ Error scoring chunk {i}: {e}")
                chunk.pedagogical_score = 0.0

            if chunk.pedagogical_score >= self.threshold:
                approved_chunks.append(chunk)

        # Sort by score descending
        approved_chunks.sort(key=lambda x: x.pedagogical_score, reverse=True)
        return approved_chunks
