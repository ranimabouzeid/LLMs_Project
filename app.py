import streamlit as st
from main_pipeline import run_pipeline

st.set_page_config(page_title="DeepStudy Coach", layout="wide")

st.title("DeepStudy Coach")
st.write("Understand, don't memorize.")

query = st.text_input("Ask a study question")

if st.button("Explain") and query:
    with st.spinner("Thinking..."):
        try:
            result = run_pipeline(query)

            st.subheader("Structured Explanation")
            st.write(result["answer"])

            st.subheader("Coverage Check")
            st.write(result["coverage"])

            with st.expander("Selected Evidence Chunks"):
                for i, item in enumerate(result["ranked_docs"][:4], start=1):
                    doc = item["doc"]
                    st.markdown(f"### Chunk {i}")
                    st.write(f"Final Score: {item['final_score']:.2f}")
                    st.write(f"Relevance Score: {item['relevance_score']:.2f}")
                    st.write(f"Evidence Quality: {item['evidence_quality']:.2f}")
                    st.write(f"Educational Usefulness: {item['educational_usefulness']:.2f}")
                    st.write(doc.page_content[:1000])
                    st.markdown("---")

        except Exception as e:
            st.error(f"Error: {e}")
