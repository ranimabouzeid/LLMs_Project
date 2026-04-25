import json
import sqlite3
from typing import Dict, Any, List
from memory.concept_debt_ledger import ConceptDebtLedger
from agents.debt_detector import detect_concept_debt
from pipeline.schemas import KeyIdea

class MemoryManager:
    """
    Orchestrates all memory updates after a student interaction.
    """
    def __init__(self, db_path="data/student.db"):
        self.db_path = db_path
        self.cdl = ConceptDebtLedger(db_path)

    def process_interaction(self, 
                            student_id: str, 
                            query: str, 
                            explanation: str, 
                            key_ideas: List[KeyIdea],
                            missing_ideas: List[str]):
        """
        Runs Step 8 of the pipeline: Update all memory layers.
        """
        print(f"🧠 [MemoryManager] Updating student profile for '{student_id}'...")
        
        # 1. Update Session History
        self._save_session(student_id, query, explanation, key_ideas)

        # 2. Detect and Save Concept Debt
        if missing_ideas:
            print(f"   ⚠️ Detecting prerequisite gaps from {len(missing_ideas)} missing ideas...")
            new_debts = detect_concept_debt(query, missing_ideas)
            if new_debts:
                self.cdl.add_debts(student_id, new_debts)
                print(f"   ✅ Recorded {len(new_debts)} new concept debts.")

        # 3. Update Weak Topics
        self._update_weak_topics(student_id, query, len(missing_ideas))

    def _save_session(self, student_id, query, explanation, key_ideas):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            summary = explanation[:200] + "..." # Simplified summary
            ideas_json = json.dumps([i.name for i in key_ideas])
            cursor.execute("""
                INSERT INTO session_history (student_id, query, summary, key_ideas_covered)
                VALUES (?, ?, ?, ?)
            """, (student_id, query, summary, ideas_json))
            conn.commit()

    def _update_weak_topics(self, student_id, topic, missing_count):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # If they missed ideas, increase difficulty score
            impact = 1.0 if missing_count > 0 else -0.5
            cursor.execute("""
                INSERT INTO weak_topics (student_id, topic, difficulty, interactions)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(student_id, topic) DO UPDATE SET
                    difficulty = MAX(0, MIN(10, difficulty + ?)),
                    interactions = interactions + 1,
                    last_seen = CURRENT_TIMESTAMP
            """, (student_id, topic, impact, impact))
            conn.commit()
