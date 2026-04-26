"""
Concept debt panel UI for TutorMind.

Displays prerequisite gaps detected for the active student.
"""

import sqlite3
from pathlib import Path

import streamlit as st

DB_PATH = Path("data/student.db")


def _get_open_debts(student_id: str) -> list[tuple]:
    """Fetch open concept debts for a student."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT topic, prerequisite_concept, severity, evidence, created_at
        FROM concept_debt
        WHERE student_id = ? AND status = 'open'
        ORDER BY severity DESC, created_at DESC
        """,
        (student_id,),
    )

    debts = cur.fetchall()
    conn.close()

    return debts


def render_debt_panel(student_id: str) -> None:
    """
    Render the concept debt sidebar panel.

    Args:
        student_id: The active student identifier from the sidebar.
    """
    st.header("Concept Debts")

    if not student_id.strip():
        st.warning("Enter a student ID to load concept debts.")
        return

    try:
        debts = _get_open_debts(student_id)
    except Exception as exc:
        st.error(f"Could not load concept debts: {exc}")
        return

    if not debts:
        st.caption("No open concept debts yet.")
        return

    for target, prerequisite, severity, evidence, created_at in debts:
        st.markdown(
            f"""
            **Missing prerequisite:** `{prerequisite}`  
            Related topic: `{target}`  
            Severity: `{severity}/5`  
            Evidence: {evidence or "No evidence recorded."}  
            _Detected: {created_at}_
            """
        )