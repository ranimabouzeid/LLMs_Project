import streamlit as st


def render_chat_window():
    question = st.chat_input("Ask a question about your course material")

    if question:
        st.chat_message("user").write(question)

        with st.chat_message("assistant"):
            st.write("Pipeline response will appear here once connected.")

            with st.expander("Sources"):
                st.write("Retrieved chunks will appear here.")

            with st.expander("Coverage Report"):
                st.write("Covered and missing key ideas will appear here.")

            with st.expander("Self-check Questions"):
                st.write("Generated questions will appear here.")

    return question