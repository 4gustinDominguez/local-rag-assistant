import streamlit as st
from config.rag_defaults import DEFAULT_RAG_CONFIG
from llm import is_cloud_model


def init_rag_config():
    if "rag_config" not in st.session_state:
        st.session_state.rag_config = DEFAULT_RAG_CONFIG.copy()


def render_rag_sidebar():
    init_rag_config()
    cfg = st.session_state.rag_config

    st.sidebar.header("RAG Configuration")

    # Local models (offline) + cloud (requires OLLAMA_API_KEY in .env)
    models = ["llama3.2:latest", "qwen2.5:7b", "gemma4:31b-cloud"]
    default_model = DEFAULT_RAG_CONFIG["model_name"]
    if default_model not in models:
        models.insert(0, default_model)

    cfg["model_name"] = st.sidebar.selectbox(
        "Model",
        models,
        index=models.index(default_model)
    )

    if is_cloud_model(cfg["model_name"]):
        st.sidebar.caption("☁️ Cloud model — needs a connection and OLLAMA_API_KEY")
    else:
        st.sidebar.caption("🏠 Local model — works offline")

    cfg["temperature"] = st.sidebar.slider(
        "Temperature",
        0.0, 1.0, cfg["temperature"], step=0.1
    )

    cfg["max_tokens"] = st.sidebar.slider(
        "Max answer tokens",
        100, 1200, cfg["max_tokens"], step=50
    )

    cfg["n_results"] = st.sidebar.slider(
        "Retrieved chunks",
        2, 12, cfg["n_results"]
    )

    cfg["top_k"] = st.sidebar.slider(
        "Chunks in prompt",
        1, 6, cfg["top_k"]
    )

    cfg["max_distance"] = st.sidebar.slider(
        "Relevance threshold",
        0.05, 0.40, cfg["max_distance"], step=0.01,
        help="Lower = stricter. Chunks less relevant than this are "
             "discarded (calibrated for multilingual-e5-large)."
    )

    cfg["use_memory"] = st.sidebar.checkbox(
        "Use short memory",
        value=cfg["use_memory"]
    )

    cfg["memory_turns"] = st.sidebar.slider(
        "Memory turns",
        1, 6, cfg["memory_turns"],
        disabled=not cfg["use_memory"]
    )

    if st.sidebar.button("Set defaults"):
        st.session_state.rag_config = DEFAULT_RAG_CONFIG.copy()
        st.sidebar.success("Defaults restored")

    return st.session_state.rag_config
