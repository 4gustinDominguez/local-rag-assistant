from rag import build_prompt

DOCS = [
    {"text": "La compuerta AND vale 1 si ambas entradas valen 1.",
     "metadata": {"source": "logica.pdf", "page": 12}},
    {"text": "El multiplexor selecciona una de varias entradas.",
     "metadata": {"source": "circuitos.pdf", "page": 41}},
]


def test_no_retrieved_documents_declares_no_material():
    prompt = build_prompt("¿Qué es?", [], memory=None)
    assert "sin documentos relevantes" in prompt


def test_grounding_rules_are_present():
    prompt = build_prompt("¿Qué es?", DOCS, memory=None)
    assert "Contexto recuperado" in prompt
    assert "No está en el material." in prompt


def test_refusal_is_demanded_when_context_is_off_topic():
    prompt = build_prompt("¿Qué es?", DOCS, memory=None)
    assert "no trata el tema de la pregunta" in prompt


def test_the_model_is_forbidden_from_inventing_sources():
    prompt = build_prompt("¿Qué es?", DOCS, memory=None)
    assert "Nunca inventes fuentes" in prompt


def test_fragments_are_labelled_for_citation():
    prompt = build_prompt("¿Qué es?", DOCS, memory=None)
    assert "[F1] logica.pdf, pág. 12" in prompt
    assert "[F2] circuitos.pdf, pág. 41" in prompt


def test_the_question_is_included():
    prompt = build_prompt("¿Qué es un multiplexor?", DOCS, memory=None)
    assert "¿Qué es un multiplexor?" in prompt


def test_conversation_history_is_included():
    prompt = build_prompt("¿Y ahora?", DOCS,
                          memory=[("Pregunta previa", "Respuesta previa")])
    assert "Pregunta previa" in prompt
    assert "Respuesta previa" in prompt


def test_no_history_block_when_memory_is_empty():
    prompt = build_prompt("¿Y ahora?", DOCS, memory=None)
    assert "Pregunta previa" not in prompt
