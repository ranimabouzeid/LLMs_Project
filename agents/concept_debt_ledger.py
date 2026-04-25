import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from schemas import DebtEntry


DB_PATH = Path("data/concept_debt_ledger.db")


class ConceptDebtLedger:
    """
    Stores, updates, retrieves, and ranks concept debt entries.

    A concept debt is a weak or missing concept that the student needs to review.
    The ledger makes these weaknesses persistent using SQLite.
    """

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        """
        Creates the concept debt table if it does not already exist.
        """

        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS concept_debts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    missing_concept TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    occurrences INTEGER NOT NULL DEFAULT 1,
                    status TEXT NOT NULL DEFAULT 'open',
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    UNIQUE(student_id, topic, missing_concept)
                )
                """
            )

            conn.commit()

    def add_debt(self, student_id: str, debt: DebtEntry):
        """
        Adds one concept debt.

        If the same student has the same missing concept again,
        the ledger updates the existing row instead of creating a duplicate.
        """

        now = datetime.now().isoformat(timespec="seconds")

        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, occurrences
                FROM concept_debts
                WHERE student_id = ?
                AND topic = ?
                AND missing_concept = ?
                """,
                (student_id, debt.topic, debt.missing_concept),
            )

            existing = cursor.fetchone()

            if existing:
                debt_id, occurrences = existing

                cursor.execute(
                    """
                    UPDATE concept_debts
                    SET occurrences = ?,
                        reason = ?,
                        severity = ?,
                        status = 'open',
                        last_seen = ?
                    WHERE id = ?
                    """,
                    (
                        occurrences + 1,
                        debt.reason,
                        debt.severity,
                        now,
                        debt_id,
                    ),
                )

            else:
                cursor.execute(
                    """
                    INSERT INTO concept_debts (
                        student_id,
                        topic,
                        missing_concept,
                        reason,
                        severity,
                        occurrences,
                        status,
                        first_seen,
                        last_seen
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student_id,
                        debt.topic,
                        debt.missing_concept,
                        debt.reason,
                        debt.severity,
                        1,
                        "open",
                        now,
                        now,
                    ),
                )

            conn.commit()

    def add_debts(self, student_id: str, debts: List[DebtEntry]):
        """
        Adds multiple concept debt entries.
        """

        for debt in debts:
            self.add_debt(student_id, debt)

    def get_open_debts(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Returns all unresolved concept debts for a student.
        """

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM concept_debts
                WHERE student_id = ?
                AND status = 'open'
                ORDER BY severity DESC, occurrences DESC, last_seen DESC
                """,
                (student_id,),
            )

            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_debts_by_topic(self, student_id: str, topic: str) -> List[Dict[str, Any]]:
        """
        Returns all concept debts for one student and one topic.
        """

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM concept_debts
                WHERE student_id = ?
                AND topic = ?
                ORDER BY severity DESC, occurrences DESC, last_seen DESC
                """,
                (student_id, topic),
            )

            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def mark_resolved(self, student_id: str, topic: str, missing_concept: str):
        """
        Marks a concept debt as resolved after the student improves.
        """

        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE concept_debts
                SET status = 'resolved'
                WHERE student_id = ?
                AND topic = ?
                AND missing_concept = ?
                """,
                (student_id, topic, missing_concept),
            )

            conn.commit()

    def rank_misconceptions(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Ranks open misconceptions by priority.

        Ranking logic:
        - Higher severity means the misconception is more serious.
        - Higher occurrences means the misconception is repeated.
        - Only open debts are ranked.

        Formula:
        priority_score = severity * 2.0 + occurrences * 1.5
        """

        open_debts = self.get_open_debts(student_id)
        ranked_debts = []

        for debt in open_debts:
            severity = debt["severity"]
            occurrences = debt["occurrences"]

            priority_score = (severity * 2.0) + (occurrences * 1.5)

            ranked_debt = dict(debt)
            ranked_debt["priority_score"] = round(priority_score, 2)

            if priority_score >= 10:
                ranked_debt["priority_level"] = "high"
            elif priority_score >= 6:
                ranked_debt["priority_level"] = "medium"
            else:
                ranked_debt["priority_level"] = "low"

            ranked_debts.append(ranked_debt)

        ranked_debts.sort(
            key=lambda debt: (
                debt["priority_score"],
                debt["severity"],
                debt["occurrences"],
                debt["last_seen"],
            ),
            reverse=True,
        )

        return ranked_debts

    def get_top_misconceptions(
        self,
        student_id: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Returns the top ranked misconceptions for a student.
        """

        ranked = self.rank_misconceptions(student_id)
        return ranked[:limit]

    def get_summary(self, student_id: str) -> Dict[str, Any]:
        """
        Returns a summary of the student's current concept debt.
        """

        open_debts = self.get_open_debts(student_id)
        ranked_debts = self.rank_misconceptions(student_id)

        total_open = len(open_debts)

        high_severity = [
            debt for debt in open_debts
            if debt["severity"] >= 4
        ]

        repeated_debts = [
            debt for debt in open_debts
            if debt["occurrences"] >= 2
        ]

        return {
            "student_id": student_id,
            "total_open_debts": total_open,
            "high_severity_count": len(high_severity),
            "repeated_debt_count": len(repeated_debts),
            "top_ranked_misconceptions": ranked_debts[:5],
        }