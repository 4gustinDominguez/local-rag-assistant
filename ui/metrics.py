import streamlit as st


def show_metrics(rag_time, llm_time, total_time):
    st.subheader("Performance")

    c1, c2, c3 = st.columns(3)
    c1.metric("Retrieval + Prompt (s)", f"{rag_time:.2f}")
    c2.metric("LLM Generation (s)", f"{llm_time:.2f}")
    c3.metric("Total (s)", f"{total_time:.2f}")
