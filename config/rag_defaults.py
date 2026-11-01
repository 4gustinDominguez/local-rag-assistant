DEFAULT_RAG_CONFIG = {
    "model_name": "llama3.2:latest",
    "temperature": 0.2,
    "max_tokens": 400,
    "n_results": 8,
    "top_k": 6,
    # Relevance threshold calibrated for multilingual-e5-large
    # (cosine distance): relevant <=0.18, irrelevant >=0.21.
    # If you change the embedding model, recalibrate it.
    "max_distance": 0.19,
    "use_memory": True,
    "memory_turns": 3,
}
