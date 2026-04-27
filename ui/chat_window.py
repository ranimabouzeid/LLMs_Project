"""
Final Polished Chat Window: MCQ Logic, Short Answers, and Silent Background Memory.
"""

import asyncio
import threading
import streamlit as st
from ui.coverage_display import render_coverage_report
from ui.source_display import render_sources
from pipeline.teaching_pipeline import pipeline
from agents.question_generator import evaluate_short_answer

def render_chat_window(student_id: str):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 1. DISPLAY HISTORY
    for msg_idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant":
                if "sources" in message: render_sources(message["sources"])
                if "coverage" in message and message["coverage"]: render_coverage_report(message["coverage"])
                
                # Render Assessments
                if "questions" in message and message["questions"]:
                    with st.expander("📝 Practice & Assessment", expanded=False):
                        # Separate MCQ and Short Answer
                        mcqs = [q for q in message["questions"] if isinstance(q, dict)]
                        short_as = [q for q in message["questions"] if isinstance(q, str)]

                        if mcqs:
                            st.subheader("Multiple Choice")
                            for i, q in enumerate(mcqs, 1):
                                st.markdown(f"**Q{i}: {q['question']}**")
                                for opt, text in q.get("options", {}).items():
                                    st.write(f"{opt}: {text}")
                                
                                # Use unique key for every question in history
                                key = f"m_{msg_idx}_q_{i}"
                                if msg_idx == len(st.session_state.messages) - 1:
                                    choice = st.selectbox(f"Select Answer (Q{i})", ["-", "A", "B", "C", "D"], key=key)
                                    if choice != "-":
                                        correct = q.get("correct_answer")
                                        logic = q.get("explanation", "No explanation provided.")
                                        is_correct = (choice == correct)
                                        
                                        if is_correct:
                                            st.success(f"✅ **Correct!** {logic}")
                                        else:
                                            st.error(f"❌ **Incorrect.** Correct answer: {correct}. \n\n{logic}")

                                        # Record mastery/struggle in background
                                        rec_key = f"rec_{key}"
                                        if rec_key not in st.session_state:
                                            threading.Thread(
                                                target=pipeline.memory.process_quiz_result,
                                                args=(student_id, message.get("query", "General"), q['question'], choice, correct, is_correct),
                                                daemon=True
                                            ).start()
                                            st.session_state[rec_key] = True
                                st.divider()

                        if short_as:
                            st.subheader("Short Answer Challenge")
                            for i, q_text in enumerate(short_as, 1):
                                st.markdown(f"**Challenge {i}: {q_text}**")
                                if msg_idx == len(st.session_state.messages) - 1:
                                    u_ans = st.text_area("Your Answer", key=f"sa_{msg_idx}_{i}")
                                    if st.button(f"Submit Answer {i}", key=f"btn_{msg_idx}_{i}"):
                                        with st.spinner("Grading..."):
                                            feedback = evaluate_short_answer(q_text, u_ans)
                                            st.info(f"👨‍🏫 **Tutor Feedback:** {feedback}")

    # 2. HANDLE NEW INPUT
    if question := st.chat_input("Ask a question about your course material"):
        with st.chat_message("user"): st.write(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing material..."):
                all_open_debts = pipeline.cdl.get_active_debts(student_id, question)
                from agents.debt_detector import filter_relevant_debts
                open_debts = filter_relevant_debts(question, all_open_debts)
                from memory.preference_memory import get_preferences
                preferences = {p[0]: p[1] for p in get_preferences(student_id)}
                
                # Cache Check
                cached = pipeline.cache.get(question)
                if cached:
                    key_ideas, approved_chunks = cached
                else:
                    search_results = pipeline.knowledge_store.search(question, k=8, filter={"student_id": student_id})
                    from pipeline.schemas import Chunk
                    raw_chunks = [Chunk(text=d.page_content, metadata=d.metadata, source_file=d.metadata.get("source_file"), page_number=d.metadata.get("page")) for d in search_results]
                    
                    # Sequential for US-Central Stability
                    approved_chunks = pipeline.judge.score_chunks(question, raw_chunks)
                    import time; time.sleep(1) # Safety gap
                    key_ideas = pipeline.decomposer.decompose(question)
                    pipeline.cache.set(question, key_ideas, approved_chunks)

            # Streaming Explanation
            explanation_container = st.empty()
            stream = pipeline.generate_explanation_stream(question, key_ideas, approved_chunks, open_debts, st.session_state.messages, preferences, True)
            full_explanation = explanation_container.write_stream(stream)

            # Final Quality Audit
            with st.status("Verifying curriculum...") as status:
                report, questions = pipeline.quality_agent.perform_final_audit(question, full_explanation, key_ideas)
                
                # Silent Background DB update
                def bg():
                    pipeline.memory.process_interaction(student_id, question, full_explanation, key_ideas, report.missing_ideas if report else [])
                    for d in open_debts: pipeline.cdl.mark_as_repaired(student_id, d.prerequisite_concept)
                threading.Thread(target=bg, daemon=True).start()
                status.update(label="Verified!", state="complete")

            st.session_state.messages.append({
                "role": "assistant", "content": full_explanation, "query": question,
                "sources": approved_chunks, "coverage": report, "questions": questions
            })
            st.rerun()
