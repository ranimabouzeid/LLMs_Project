"""
Source display UI for TutorMind.

Renders retrieved document chunks and their optional retrieval judge scores.
"""

from typing import Any, Iterable, Optional

import streamlit as st


def _get_value(source: Any, key: str, default: Any = None) -> Any:
    """
    Read a value from either a dictionary-like source or an object attribute.
    This keeps the UI compatible with future Chunk dataclasses.
    """
    if isinstance(source, dict):
        return source.get(key, default)

    return getattr(source, key, default)


def render_sources(sources: Optional[Iterable[Any]] = None) -> None:
    """
    Render retrieved sources in an expandable section.

    Args:
        sources: Optional iterable of source chunks. Each item can be a dict
                 or an object with fields such as text, source, page, and tarj_score.
    """
    with st.expander("Sources", expanded=False):
        if not sources:
            st.caption("No retrieved sources yet.")
            return

        for index, source in enumerate(sources, start=1):
            source_name = _get_value(source, "source", "Unknown source")
            page = _get_value(source, "page")
            score = _get_value(source, "tarj_score")
            text = _get_value(source, "text", "")

            title = f"Source {index}: {source_name}"
            if page is not None:
                title += f" — page {page}"

            st.markdown(f"**{title}**")

            if score is not None:
                st.caption(f"TARJ score: {float(score):.1f}/10")

            if text:
                st.write(text)
            else:
                st.caption("No source text available.")

            st.divider()