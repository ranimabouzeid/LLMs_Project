"""
Coverage report UI for TutorMind.

Displays which key ideas were covered, partially covered, or missed by the explanation.
"""

from typing import Any, Iterable, Optional

import streamlit as st


def _get_value(report: Any, key: str, default: Any = None) -> Any:
    """
    Read a value from either a dictionary-like report or an object attribute.
    This keeps the UI compatible with future CoverageReport dataclasses.
    """
    if isinstance(report, dict):
        return report.get(key, default)

    return getattr(report, key, default)


def _render_list(title: str, items: Optional[Iterable[str]]) -> None:
    """Render a titled list of coverage items."""
    st.markdown(f"**{title}**")

    if not items:
        st.caption("None")
        return

    for item in items:
        st.write(f"- {item}")


def render_coverage_report(report: Optional[Any] = None) -> None:
    """
    Render explanation coverage information.

    Args:
        report: Optional coverage report. Can be a dict or an object with:
                covered, partial, missing, supplement_added, supplement_text.
    """
    with st.expander("Coverage Report", expanded=False):
        if report is None:
            st.caption("No coverage report yet.")
            return

        covered = _get_value(report, "covered_ideas", [])
        missing = _get_value(report, "missing_ideas", [])
        supplement_added = bool(_get_value(report, "supplement", False))
        supplement_text = _get_value(report, "supplement", None)
        feedback = _get_value(report, "feedback", None)

        _render_list("Covered Key Ideas", covered)
        _render_list("Missing Key Ideas", missing)

        if feedback:
            st.markdown("**Pedagogical Feedback**")
            st.write(feedback)

        st.markdown("**Supplement Added**")
        st.write("Yes" if supplement_added else "No")

        if supplement_text:
            st.markdown("**Supplement Text**")
            st.write(supplement_text)