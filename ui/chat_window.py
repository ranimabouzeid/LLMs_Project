"""
Chat window UI for TutorMind.

Currently renders a placeholder response until the full teaching pipeline
is connected by the pipeline owner.
"""

from typing import Optional

import streamlit as st

from ui.coverage_display import render_coverage_report
from ui.source_display import render_sources


def render_chat_window() -> Optional[str]:
    """
    Render the chat input and placeholder assistant response.

    Returns:
        The latest user question, or None if no question was submitted.
    """
    question = st.chat_input("Ask a question about your course material")

    if not question:
        return None

    st.chat_message("user").write(question)

    with st.chat_message("assistant"):
        st.write("Pipeline response will appear here once connected.")

        render_sources()
        render_coverage_report()

        with st.expander("Self-check Questions"):
            st.write("Generated questions will appear here.")

    return question