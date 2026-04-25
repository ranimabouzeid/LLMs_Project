"""
Upload panel UI for TutorMind.

Handles course material uploads and saves files locally for later ingestion.
"""

from pathlib import Path
from typing import List

import streamlit as st

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


def render_upload_panel() -> List[Path]:
    """
    Render the upload panel and save uploaded course files.

    Returns:
        A list of saved file paths.
    """
    st.header("Upload Course Material")

    uploaded_files = st.file_uploader(
        "Upload PDF, PPTX, or DOCX",
        type=list(ALLOWED_EXTENSIONS),
        accept_multiple_files=True,
    )

    saved_paths: List[Path] = []

    if not uploaded_files:
        st.caption("No files uploaded yet.")
        return saved_paths

    for uploaded_file in uploaded_files:
        file_extension = Path(uploaded_file.name).suffix.lower().replace(".", "")

        if file_extension not in ALLOWED_EXTENSIONS:
            st.error(f"Unsupported file type: {uploaded_file.name}")
            continue

        try:
            saved_path = _save_uploaded_file(uploaded_file)
            saved_paths.append(saved_path)
            st.success(f"Saved: {saved_path.name}")
        except Exception as exc:
            st.error(f"Could not save {uploaded_file.name}: {exc}")

    return saved_paths