import json
from typing import List
from pipeline.schemas import Chunk
from tools.llm_client import llm_client

class RetrievalJudge:
    """
    TARJ: Technical & Academic Retrieval Judge.
    Uses batching to stay within Google Cloud Quota limits.
    """
    def __init__(self, threshold: float = 5.0):
        self.threshold = threshold

    def score_chunks(self, query: str, chunks: List[Chunk]) -> List[Chunk]:
        """
        Scores all chunks in a single batch to save quota.
        """
        if not chunks:
            return []

        print(f"⏳ Starting BATCH TARJ Judging for {len(chunks)} chunks...")

        system_prompt = """
        You are a pedagogical expert. Evaluate the following text chunks 
        for their usefulness in answering a student's query.
        
        For each chunk, provide a score from 0.0 to 10.0.
        - 10.0: Perfectly explains the core concept with deep intuition.
        - 5.0: Provides facts but lacks pedagogical depth.
        - 0.0: Irrelevant, code-only, or garbage text.
        
        Return your response in EXACT JSON format:
        {"scores": [8.5, 4.0, 0.0, ...]}
        """

        # Format chunks for a single prompt
        chunks_text = ""
        for i, chunk in enumerate(chunks):
            chunks_text += f"\n--- CHUNK {i} ---\n{chunk.text}\n"

        user_message = f"QUERY: {query}\n\nCHUNKS TO EVALUATE: {chunks_text}"

        try:
            response = llm_client.chat(system_prompt, user_message, json_mode=True)
            scores = response.get("scores", [])

            approved = []
            for i, chunk in enumerate(chunks):
                # Match score to chunk, default to 0 if list is too short
                score = scores[i] if i < len(scores) else 0.0
                chunk.pedagogical_score = float(score)
                
                if chunk.pedagogical_score >= self.threshold:
                    print(f"  ✅ Chunk {i} Approved: {chunk.pedagogical_score}/10.0")
                    approved.append(chunk)
                else:
                    print(f"  ❌ Chunk {i} Rejected: {chunk.pedagogical_score}/10.0")

            return approved

        except Exception as e:
            print(f"  ⚠️ Batch Judging failed: {e}. Falling back to empty list.")
            return []
