import json
import sqlite3
import time
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
        Runs Step 8 of the pipeline (Post-Explanation Logging).
        """
        try:
            self._save_session(student_id, query, explanation, key_ideas)
            if missing_ideas:
                new_debts = detect_concept_debt(query, missing_ideas)
                if new_debts:
                    self.cdl.add_debts(student_id, new_debts)
            self._update_weak_topics(student_id, query, len(missing_ideas))
        except Exception as e:
            print(f"❌ [MemoryManager] interaction update failed: {e}")

    def process_quiz_result(self, student_id: str, topic: str, question: str, student_answer: str, correct_answer: str, is_correct: bool):
        """
        Updates memory based on a specific quiz question outcome.
        """
        print(f"🧠 [MemoryManager] Processing quiz result for '{student_id}' (Correct: {is_correct})")
        try:
            if not is_correct:
                # 1. If wrong, detect what prerequisite is missing
                evidence = f"Student answered '{student_answer}' instead of '{correct_answer}' for: {question[:100]}..."
                new_debts = detect_concept_debt(topic, [evidence])
                if new_debts:
                    self.cdl.add_debts(student_id, new_debts)
                    print(f"   💸 Added debt based on wrong quiz answer.")
            
            # 2. Update topic difficulty
            impact = -1.0 if is_correct else 1.0 # Significant reward for correct quiz answers
            self._update_weak_topics(student_id, topic, 0, custom_impact=impact)
            
        except Exception as e:
            print(f"❌ [MemoryManager] Quiz update failed: {e}")

    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def _save_session(self, student_id, query, explanation, key_ideas):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            summary = explanation[:200].replace("\n", " ") + "..."
            ideas_json = json.dumps([i.name for i in key_ideas])
            cursor.execute("""
                INSERT INTO session_history (student_id, query, summary, key_ideas_covered)
                VALUES (?, ?, ?, ?)
            """, (student_id, query, summary, ideas_json))
            conn.commit()

    def _update_weak_topics(self, student_id, topic, missing_count, custom_impact=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if custom_impact is not None:
                impact = custom_impact
            else:
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
