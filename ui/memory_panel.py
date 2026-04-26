"""
Memory panel UI for TutorMind with manual preference overrides.
"""

from typing import Any
import streamlit as st
from memory.preference_memory import get_preferences, save_preference
from memory.session_history import get_recent_sessions
from memory.weak_topic_tracker import get_weak_topics

def _render_weak_topics(student_id: str) -> None:
    st.subheader("📈 Knowledge Map")
    try:
        weak_topics = get_weak_topics(student_id)
        if not weak_topics:
            st.caption("No weak topics recorded yet.")
            return
        for topic, diff, inter, last in weak_topics:
            st.markdown(f"**{topic}** (Difficulty: `{diff:.1f}/10`)")
    except Exception as e:
        st.error(f"Error: {e}")

def _render_preferences(student_id: str) -> None:
    st.subheader("⚙️ Learning Settings")
    
    # 1. Manual Override Form
    with st.form("pref_form"):
        st.write("Customize your tutor's behavior:")
        depth = st.selectbox("Explanation Depth", ["Balanced", "Concise (Just the facts)", "Detailed (Deep dive)"])
        format_style = st.selectbox("Formatting", ["Mixed (Prose + Bullets)", "Bullet Points Only", "Academic Prose"])
        
        submitted = st.form_submit_button("Save Preferences")
        if submitted:
            save_preference(student_id, "explanation_depth", depth)
            save_preference(student_id, "format_style", format_style)
            st.success("Preferences updated!")

    # 2. Display Current
    st.write("---")
    st.write("**Active Preferences:**")
    prefs = get_preferences(student_id)
    if not prefs:
        st.caption("No preferences stored yet.")
    for key, val, conf in prefs:
        st.markdown(f"- {key.replace('_', ' ').title()}: `{val}`")

def _render_recent_sessions(student_id: str) -> None:
    st.subheader("🕒 Session History")
    try:
        sessions = get_recent_sessions(student_id)
        if not sessions:
            st.caption("No sessions found.")
            return
        for topic, summary, date in sessions:
            st.markdown(f"**{topic}**: {summary[:100]}... \n_{date}_")
    except Exception as e:
        st.error(f"Error: {e}")

def render_memory_panel(student_id: str) -> None:
    """
    Render the full student memory panel. (Header removed for sidebar consistency)
    """
    if not student_id.strip():
        return

    with st.expander("📊 Knowledge & Preferences", expanded=False):
        _render_weak_topics(student_id)
        st.divider()
        _render_preferences(student_id)
        st.divider()
        _render_recent_sessions(student_id)
