"""
Source display UI for TutorMind.
Renders retrieved document chunks and their optional retrieval judge scores.
"""

from typing import Any, Iterable, Optional
import streamlit as st

def _get_value(source: Any, key_list: list, default: Any = None) -> Any:
    """
    Tries to find a value from a list of possible keys in both dict and object formats.
    """
    for key in key_list:
        if isinstance(source, dict):
            val = source.get(key)
            if val is not None: return val
        else:
            val = getattr(source, key, None)
            if val is not None: return val
    return default

def render_sources(sources: Optional[Iterable[Any]] = None) -> None:
    """
    Render retrieved sources in an expandable section.
    """
    with st.expander("Sources", expanded=False):
        if not sources:
            st.caption("No retrieved sources yet (or quality threshold not met).")
            return

        for index, source in enumerate(sources, start=1):
            # Check all possible naming conventions to avoid "Unknown Source"
            source_name = _get_value(source, ["source_file", "source", "filename"], "Unknown source")
            page = _get_value(source, ["page_number", "page"])
            score = _get_value(source, ["pedagogical_score", "tarj_score", "score"])
            text = _get_value(source, ["text", "page_content", "content"], "")

            title = f"Source {index}: {source_name}"
            if page is not None and str(page) != "":
                title += f" — page {page}"

            st.markdown(f"**{title}**")

            if score is not None:
                st.caption(f"Pedagogical Quality: {float(score):.1f}/10")

            if text:
                st.write(text)
            else:
                st.caption("No source text available.")

            st.divider()
