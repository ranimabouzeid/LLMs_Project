import sqlite3
import json
import hashlib
from typing import Optional, Tuple, List
from pipeline.schemas import KeyIdea, Chunk

DB_PATH = "data/student.db"

class KnowledgeCache:
    """
    Semantic caching layer to speed up the pipeline.
    Stores (Query -> KeyIdeas, ApprovedChunks) to skip redundant LLM work.
    """
    
    def _get_hash(self, text: str) -> str:
        clean_text = text.lower().strip().replace("?", "").replace(".", "")
        return hashlib.md5(clean_text.encode()).hexdigest()

    def get(self, query: str) -> Optional[Tuple[List[KeyIdea], List[Chunk]]]:
        """Returns cached results if they exist."""
        q_hash = self._get_hash(query)
        try:
            with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
                cur = conn.cursor()
                cur.execute("SELECT key_ideas_json, approved_chunks_json FROM knowledge_cache WHERE query_hash = ?", (q_hash,))
                row = cur.fetchone()
                
                if row:
                    print("\n" + "⚡"*30)
                    print(f"🚀 CACHE HIT: Found existing thought-process for: '{query[:50]}'")
                    print("⏩ SKIPPING Steps 3 & 4 (Judging & Decomposition)...")
                    print("⚡"*30 + "\n")
                    
                    ideas_raw = json.loads(row[0])
                    ideas = [KeyIdea(**i) for i in ideas_raw]
                    chunks_raw = json.loads(row[1])
                    chunks = [Chunk(**c) for c in chunks_raw]
                    return ideas, chunks
                else:
                    print(f"\n❄️  CACHE MISS: Generating new curriculum decomposition for: '{query[:50]}'...")
        except Exception as e:
            print(f"⚠️ Cache get error: {e}")
        return None

    def set(self, query: str, key_ideas: List[KeyIdea], chunks: List[Chunk]):
        """Stores the thought process in the cache."""
        q_hash = self._get_hash(query)
        try:
            ideas_json = json.dumps([i.dict() for i in key_ideas])
            chunks_json = json.dumps([c.dict() for c in chunks])
            
            with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO knowledge_cache (query_hash, key_ideas_json, approved_chunks_json)
                    VALUES (?, ?, ?)
                """, (q_hash, ideas_json, chunks_json))
                conn.commit()
                print(f"💾 CACHE STORED: Optimization saved for future queries of '{query[:30]}'.")
        except Exception as e:
            print(f"⚠️ Cache set error: {e}")
