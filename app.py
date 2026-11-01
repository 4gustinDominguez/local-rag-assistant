import os
import time

import streamlit as st

from chat_store import list_chat_dates, load_chat, save_turn
from ingest import ingest_uploaded_file
from llm import ask_llm
from memory import add_to_memory, get_memory, init_memory
from rag import resolve_citations, run_rag
from subjects_manager import create_subject, list_documents
from ui.metrics import show_metrics
from ui.rag_sidebar import render_rag_sidebar
from utils.latex import autolatex, render_answer_with_latex

cfg = render_rag_sidebar()
init_memory(st)

st.title("Asistente RAG – Estudios Universitarios")

# ---------- Subjects ----------
st.sidebar.header("Asignaturas")

new_subject = st.sidebar.text_input("Crear nueva asignatura")

if st.sidebar.button("Crear"):
    if new_subject.strip():
        create_subject(new_subject.strip().lower())
        st.sidebar.success(f"Asignatura creada: {new_subject}")
    else:
        st.sidebar.error("Nombre no válido.")

subjects = [d for d in os.listdir("subjects") if os.path.isdir(f"subjects/{d}")]
if not subjects:
    st.warning("No hay asignaturas. Creá una desde la barra lateral.")
    st.stop()

selected_subject = st.sidebar.selectbox("Seleccionar asignatura", subjects)

# ---------- Document ingestion ----------
st.header("Ingesta de documentos")

uploaded_files = st.file_uploader(
    "Subir PDFs",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    for f in uploaded_files:
        fname = ingest_uploaded_file(f, selected_subject)
        st.success(f"📄 '{fname}' indexado en {selected_subject}.")

st.subheader("Documentos en Base de Conocimientos")
existing_docs = list_documents(selected_subject)
if existing_docs:
    for d in existing_docs:
        st.caption(f"📚 {d}")
else:
    st.info("No hay documentos indexados aún.")


# ---------- RAG questions ----------
st.header("Consultar al Asistente")

question = st.text_input("Pregunta:")

if st.button("Consultar") and question:
    start_total = time.perf_counter()

    memory = (
        get_memory(st, selected_subject)[:cfg["memory_turns"]]
        if cfg["use_memory"]
        else []
    )

    start_rag = time.perf_counter()
    prompt, docs = run_rag(question, selected_subject, memory, cfg)
    rag_time = time.perf_counter() - start_rag

    start_llm = time.perf_counter()
    answer = ask_llm(
        prompt,
        model=cfg["model_name"],
        temperature=cfg["temperature"],
        max_tokens=cfg["max_tokens"],
    )
    answer = resolve_citations(answer, docs)
    answer = autolatex(answer)
    llm_time = time.perf_counter() - start_llm

    total_time = time.perf_counter() - start_total

    add_to_memory(st, selected_subject, question, answer)

    save_turn(
        subject=selected_subject,
        question=question,
        answer=answer,
        docs=docs
    )

    st.subheader("Respuesta")
    render_answer_with_latex(answer)

    show_metrics(rag_time, llm_time, total_time)

    st.subheader("Fuentes consultadas (ordenadas por relevancia)")

    for d in docs:
        meta = d.get("metadata", {}) or {}
        score = d.get("score", None)

        title = f"{meta.get('source', 'Documento')} – pág. {meta.get('page', '?')}"
        if score is not None:
            title += f" | score {score:.3f}"

        with st.expander(title):
            st.write(d["text"])

# ---------- Chat history ----------
st.header("Historial de chats")

chat_dates = list_chat_dates(selected_subject)

if not chat_dates:
    st.info("No hay chats guardados para esta asignatura.")
else:
    selected_date = st.selectbox(
        "Seleccionar fecha",
        chat_dates
    )

    if selected_date:
        content = load_chat(selected_subject, selected_date)

        st.subheader(f"Chat del {selected_date}")
        st.markdown(content)
