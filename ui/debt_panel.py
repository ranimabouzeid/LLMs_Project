"""
Concept debt panel UI for TutorMind.
Displays prerequisite gaps detected for the active student in an expandable menu.
"""

import sqlite3
from pathlib import Path
import streamlit as st

DB_PATH = Path("data/student.db")

def _get_open_debts(student_id: str) -> list:
    """Fetch open concept debts for a student."""
    try:
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
    except Exception as e:
        print(f"Error fetching debts: {e}")
        return []

def render_debt_panel(student_id: str) -> None:
    """
    Render the concept debt sidebar panel as an expander.
    """
    if not student_id.strip():
        return

    with st.expander("💸 Concept Debt Ledger", expanded=True):
        try:
            debts = _get_open_debts(student_id)
        except Exception as exc:
            st.error(f"Could not load concept debts: {exc}")
            return

        if not debts:
            st.caption("No open concept debts yet. You're fully caught up!")
            return

        for target, prerequisite, severity, evidence, created_at in debts:
            st.markdown(
                f"""
                **Missing prerequisite:** `{prerequisite}`  
                *Related to:* {target}  
                *Severity:* `{severity}/5`  
                ---
                """
            )
            if evidence:
                st.caption(f"Evidence: {evidence}")
            st.write("") # Spacer
