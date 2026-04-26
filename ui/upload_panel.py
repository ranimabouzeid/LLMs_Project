"""
Upload panel UI for TutorMind.
Handles course material uploads and indexes them into ChromaDB.
"""

from pathlib import Path
from typing import List
import streamlit as st

from tools.document_loader import load_document
from tools.chunker import chunk_loaded_pages
from tools.embedder import ChromaEmbedder

UPLOAD_DIR = Path("data/uploads")
ALLOWED_EXTENSIONS = {"pdf", "pptx", "docx"}

def _save_uploaded_file(uploaded_file) -> Path:
    """Save a Streamlit uploaded file to the local uploads directory."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(uploaded_file.name).name
    file_path = UPLOAD_DIR / safe_name
    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    return file_path

def render_upload_panel(student_id: str) -> None:
    """
    Render the upload panel and allow immediate indexing.
    """
    st.header("Upload Material")

    uploaded_files = st.file_uploader(
        "Upload PDF, PPTX, or DOCX",
        type=list(ALLOWED_EXTENSIONS),
        accept_multiple_files=True,
    )

    if uploaded_files:
        if st.button("Index Documents"):
            with st.spinner("Indexing your documents..."):
                all_chunks = []
                for uploaded_file in uploaded_files:
                    try:
                        file_path = _save_uploaded_file(uploaded_file)
                        
                        # Load and tag with student_id
                        pages = load_document(str(file_path))
                        for page in pages:
                            page["student_id"] = student_id
                        
                        # Create semantic chunks
                        chunks = chunk_loaded_pages(pages)
                        all_chunks.extend(chunks)
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")

                if all_chunks:
                    db = ChromaEmbedder()
                    db.add_chunks(all_chunks)
                    st.success(f"Successfully indexed {len(all_chunks)} chunks for {student_id}!")
                else:
                    st.warning("No text extracted from documents.")
