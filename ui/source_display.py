import streamlit as st


def render_sources(sources=None):
    with st.expander("Sources"):
        if sources:
            for source in sources:
                st.write(source)
        else:
            st.write("Retrieved chunks will appear here.")