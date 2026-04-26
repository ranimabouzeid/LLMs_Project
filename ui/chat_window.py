"""
Chat window UI for TutorMind with Async support and High-Performance MCQs.
"""

import asyncio
from typing import Optional
import streamlit as st
from ui.coverage_display import render_coverage_report
from ui.source_display import render_sources
from pipeline.teaching_pipeline import pipeline
from agents.question_generator import evaluate_short_answer

def render_chat_window(student_id: str):
    """
    Renders the chat interface and maintains a history of the conversation.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg_idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            if message["role"] == "assistant":
                if "sources" in message: render_sources(message["sources"])
                if "coverage" in message: render_coverage_report(message["coverage"])
                
                if "questions" in message:
                    with st.expander("📝 Practice & Assessment", expanded=False):
                        mcqs = [q for q in message["questions"] if isinstance(q, dict)]
                        short_as = [q for q in message["questions"] if isinstance(q, str)]

                        if mcqs:
                            st.subheader("Multiple Choice Questions")
                            for i, q in enumerate(mcqs, 1):
                                st.markdown(f"**Q{i}: {q['question']}**")
                                for opt, text in q.get("options", {}).items():
                                    st.write(f"{opt}: {text}")
                                
                                if msg_idx == len(st.session_state.messages) - 1:
                                    user_choice = st.selectbox(f"Your choice for Q{i}", ["-", "A", "B", "C", "D"], key=f"msg_{msg_idx}_q_{i}")
                                    
                                    if user_choice != "-":
                                        correct = q.get("correct_answer")
                                        is_correct = (user_choice == correct)
                                        
                                        # Display result INSTANTLY
                                        if is_correct:
                                            st.success(f"✅ **Correct!** Logic: {q.get('explanation')}")
                                        else:
                                            st.error(f"❌ **Incorrect.** The correct answer was {correct}. Logic: {q.get('explanation')}")

                                        # Update memory in the background
                                        if f"recorded_{msg_idx}_q_{i}" not in st.session_state:
                                            pipeline.memory.process_quiz_result(
                                                student_id=student_id,
                                                topic=message.get("query", "General"),
                                                question=q['question'],
                                                student_answer=user_choice,
                                                correct_answer=correct,
                                                is_correct=is_correct
                                            )
                                            st.session_state[f"recorded_{msg_idx}_q_{i}"] = True
                                st.divider()

    # Handle new input
    if question := st.chat_input("Ask a question about your course material"):
        with st.chat_message("user"): st.write(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("TutorMind is thinking (Parallel Mode)..."):
                try:
                    # Run the pipeline ASYNC
                    result = asyncio.run(pipeline.run_pipeline(
                        question, 
                        student_id=student_id, 
                        history=st.session_state.messages
                    ))
                    
                    assistant_msg = {
                        "role": "assistant",
                        "content": result["explanation"],
                        "query": question,
                        "sources": result["sources"],
                        "coverage": result["coverage"],
                        "questions": result.get("questions", [])
                    }
                    st.session_state.messages.append(assistant_msg)
                    st.rerun() 
                except Exception as e:
                    st.error(f"Error: {str(e)}")
