import sqlite3
from pathlib import Path
from typing import List
from pipeline.schemas import DebtEntry

DB_PATH = Path("data/student.db")

class ConceptDebtLedger:
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path

    def _get_connection(self):
        # Increased timeout to handle background threading
        return sqlite3.connect(self.db_path, timeout=30.0)

    def get_active_debts(self, student_id: str, topic: str) -> List[DebtEntry]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT topic, prerequisite_concept, severity, evidence
                FROM concept_debt
                WHERE student_id = ? AND status = 'open'
            """, (student_id,))
            rows = cur.fetchall()
            return [DebtEntry(topic=r[0], prerequisite_concept=r[1], severity=r[2], evidence=r[3]) for r in rows]

    def add_debts(self, student_id: str, debts: List[DebtEntry]):
        with self._get_connection() as conn:
            cur = conn.cursor()
            for debt in debts:
                cur.execute("""
                    INSERT INTO concept_debt (student_id, topic, prerequisite_concept, severity, evidence, status)
                    VALUES (?, ?, ?, ?, ?, 'open')
                    ON CONFLICT(student_id, topic, prerequisite_concept) DO UPDATE SET
                        severity = MIN(5, severity + 1),
                        status = 'open',
                        updated_at = CURRENT_TIMESTAMP
                """, (student_id, debt.topic, debt.prerequisite_concept, debt.severity, debt.evidence))
            conn.commit()

    def repair_debt(self, student_id: str, topic: str):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, severity FROM concept_debt WHERE student_id = ? AND status = 'open'", (student_id,))
            rows = cur.fetchall()
            for debt_id, current_severity in rows:
                new_severity = current_severity - 1
                if new_severity <= 0:
                    cur.execute("UPDATE concept_debt SET severity = 0, status = 'repaired' WHERE id = ?", (debt_id,))
                else:
                    cur.execute("UPDATE concept_debt SET severity = ? WHERE id = ?", (new_severity, debt_id))
            conn.commit()

    def mark_as_repaired(self, student_id: str, prerequisite_concept: str):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE concept_debt 
                SET status = 'repaired', severity = 0, updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ? AND prerequisite_concept = ?
            """, (student_id, prerequisite_concept))
            conn.commit()
