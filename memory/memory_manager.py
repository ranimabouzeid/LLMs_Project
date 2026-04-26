import json
from typing import Dict, Any, List
from memory.concept_debt_ledger import ConceptDebtLedger
from agents.debt_detector import detect_concept_debt
from memory.weak_topic_tracker import update_topic_score
from memory.session_history import append_session
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
            # Save session using standardized function
            summary = explanation[:200].replace("\n", " ") + "..."
            ideas_list = [i.name for i in key_ideas]
            append_session(student_id, query, summary, ideas_list)

            # Update debts if ideas missing
            if missing_ideas:
                new_debts = detect_concept_debt(query, missing_ideas)
                if new_debts:
                    self.cdl.add_debts(student_id, new_debts)
            
            # Update topic difficulty
            impact = 1.0 if missing_ideas else -0.5
            update_topic_score(student_id, query, impact)

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
                evidence = f"Student answered '{student_answer}' instead of '{correct_answer}' for quiz question on {topic}"
                new_debts = detect_concept_debt(topic, [evidence])
                if new_debts:
                    self.cdl.add_debts(student_id, new_debts)
                    print(f"   💸 Added debt based on wrong quiz answer.")
            
            # 2. Update topic difficulty using standardized function
            impact = -1.0 if is_correct else 1.0 
            update_topic_score(student_id, topic, impact)
            
            # 3. If correct, repair debt
            if is_correct:
                self.cdl.repair_debt(student_id, topic)
            
        except Exception as e:
            print(f"❌ [MemoryManager] Quiz update failed: {e}")
