import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
from memory.db_init import init_db
from ui.upload_panel import render_upload_panel
from ui.chat_window import render_chat_window
from ui.debt_panel import render_debt_panel
from ui.memory_panel import render_memory_panel

st.set_page_config(page_title="TutorMind", layout="wide")

st.title("TutorMind")
st.caption("Teaching-aware LLM tutor with RAG and student memory")

with st.sidebar:
    st.header("Student")
    student_id = st.text_input("Student ID", value="student_001")

    # STUDENT ISOLATION LOGIC
    if "active_student" not in st.session_state:
        st.session_state.active_student = student_id
    
    if st.session_state.active_student != student_id:
        # Student changed! Clear everything to prevent data leakage
        st.session_state.messages = []
        st.session_state.active_student = student_id
        st.info(f"🔄 Switched to profile: {student_id}. History cleared.")
        st.rerun()

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    render_upload_panel(student_id)
    render_debt_panel(student_id)
    render_memory_panel(student_id)

render_chat_window(student_id)