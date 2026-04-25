import streamlit as st


def render_coverage_report(report=None):
    with st.expander("Coverage Report"):
        if report:
            st.write(report)
        else:
            st.write("Covered and missing key ideas will appear here.")