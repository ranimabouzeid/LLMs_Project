"""
Memory panel UI for TutorMind.

Displays persistent student memory:
- weak topics
- saved preferences
- recent session summaries
"""

from typing import Any

import streamlit as st

from memory.preference_memory import get_preferences
from memory.session_history import get_recent_sessions
from memory.weak_topic_tracker import get_weak_topics


def _format_empty_message(message: str) -> None:
    """Render a consistent empty-state message."""
    st.caption(message)


def _render_weak_topics(student_id: str) -> None:
    """Render weak topics for the selected student."""
    st.subheader("Weak Topics")

    try:
        weak_topics = get_weak_topics(student_id)
    except Exception as exc:
        st.error(f"Could not load weak topics: {exc}")
        return

    if not weak_topics:
        _format_empty_message("No weak topics recorded yet.")
        return

    for topic, difficulty, interactions, last_seen in weak_topics:
        difficulty_value = float(difficulty)

        st.markdown(
            f"""
            **{topic}**  
            Difficulty: `{difficulty_value:.1f}/10`  
            Interactions: `{interactions}`  
            Last seen: `{last_seen}`
            """
        )


def _render_preferences(student_id: str) -> None:
    """Render stored student preferences."""
    st.subheader("Preferences")

    try:
        preferences = get_preferences(student_id)
    except Exception as exc:
        st.error(f"Could not load preferences: {exc}")
        return

    if not preferences:
        _format_empty_message("No learning preferences stored yet.")
        return

    for key, value, confidence in preferences:
        confidence_value = float(confidence)

        st.markdown(
            f"""
            **{key}**: `{value}`  
            Confidence: `{confidence_value:.1f}`
            """
        )


def _render_recent_sessions(student_id: str) -> None:
    """Render recent session history."""
    st.subheader("Recent Sessions")

    try:
        sessions = get_recent_sessions(student_id)
    except Exception as exc:
        st.error(f"Could not load session history: {exc}")
        return

    if not sessions:
        _format_empty_message("No previous sessions found.")
        return

    for topic, summary, created_at in sessions:
        topic_label = topic if topic else "General"

        st.markdown(
            f"""
            **{topic_label}**  
            {summary}  
            _{created_at}_
            """
        )


def render_memory_panel(student_id: str) -> None:
    """
    Render the full student memory panel.

    Args:
        student_id: The active student identifier from the sidebar.
    """
    st.header("Memory")

    if not student_id.strip():
        st.warning("Enter a student ID to load memory.")
        return

    with st.expander("Weak Topics", expanded=False):
        _render_weak_topics(student_id)

    with st.expander("Preferences", expanded=False):
        _render_preferences(student_id)

    with st.expander("Recent Sessions", expanded=False):
        _render_recent_sessions(student_id)