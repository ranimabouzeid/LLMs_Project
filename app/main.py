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

init_db()

st.title("TutorMind")
st.caption("Teaching-aware LLM tutor with RAG and student memory")

with st.sidebar:
    st.header("Student")
    student_id = st.text_input("Student ID", value="student_001")

    render_upload_panel()
    render_debt_panel()
    render_memory_panel()

render_chat_window()