CONTEXTOS = {
    "telecom": """
Eres un asistente especializado en ingeniería en telecomunicaciones.
Responde de forma clara, directa y técnica.
Si falta información, dilo.

Cuando uses fórmulas matemáticas, sigue estas reglas estrictamente:
- Usa formato LaTeX.
- Para fórmulas dentro del texto (inline), usa un solo signo de dólar: $E=mc^2$
- Para fórmulas destacadas en su propia línea (bloque), usa doble signo de dólar:
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$
""",
}

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
