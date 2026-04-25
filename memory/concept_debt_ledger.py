import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from pipeline.schemas import DebtEntry

DB_PATH = Path("data/student.db")

class ConceptDebtLedger:
    """
    Manages persistent 'Concept Debt' in the master student database.
    """
    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = Path(db_path)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def add_debts(self, student_id: str, debts: List[DebtEntry]):
        """Saves new debts or updates existing ones."""
        with self._connect() as conn:
            cursor = conn.cursor()
            for debt in debts:
                cursor.execute("""
                    INSERT INTO concept_debt (student_id, topic, prerequisite_concept, severity, evidence)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, topic, prerequisite_concept) DO UPDATE SET
                        severity = excluded.severity,
                        evidence = excluded.evidence,
                        status = 'open',
                        updated_at = CURRENT_TIMESTAMP
                """, (student_id, debt.topic, debt.prerequisite_concept, debt.severity, debt.evidence))
            conn.commit()

    def get_active_debts(self, student_id: str, topic: str) -> List[DebtEntry]:
        """Retrieves unresolved debts related to a specific topic."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT prerequisite_concept, severity, evidence
                FROM concept_debt
                WHERE student_id = ? AND topic = ? AND status != 'repaired'
                ORDER BY severity DESC
            """, (student_id, topic))
            rows = cursor.fetchall()
            
            return [
                DebtEntry(
                    topic=topic,
                    prerequisite_concept=row["prerequisite_concept"],
                    severity=row["severity"],
                    evidence=row["evidence"]
                ) for row in rows
            ]

    def mark_repaired(self, student_id: str, prerequisite_concept: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE concept_debt SET status = 'repaired', updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ? AND prerequisite_concept = ?
            """, (student_id, prerequisite_concept))
            conn.commit()
