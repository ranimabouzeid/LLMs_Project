import streamlit as st

def render_upload_panel():
    st.header("Upload Course Material")

    uploaded_files = st.file_uploader(
        "Upload PDF, PPTX, or DOCX",
        type=["pdf", "pptx", "docx"],
        accept_multiple_files=True
    )

    return uploaded_files