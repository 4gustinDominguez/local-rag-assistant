from rag import resolve_citations

DOCS = [
    {"metadata": {"source": "logica.pdf", "page": 5}},
    {"metadata": {"source": "circuitos.pdf", "page": 41}},
]


def test_resolves_a_valid_citation():
    assert resolve_citations("La salida vale 1 [F1].", DOCS) == (
        "La salida vale 1 [logica.pdf, pág. 5]."
    )


def test_resolves_several_citations():
    result = resolve_citations("Vea [F1] y tambien [F2].", DOCS)
    assert "[logica.pdf, pág. 5]" in result
    assert "[circuitos.pdf, pág. 41]" in result


def test_out_of_range_citation_is_dropped():
    """The model must not be able to point at a chunk that was not given."""
    result = resolve_citations("Vea [F9].", DOCS)
    assert "[F9]" not in result
    assert "F9" not in result


def test_out_of_range_citation_leaves_no_double_space():
    assert resolve_citations("Solo [F9] inventada.", DOCS) == "Solo inventada."


def test_text_without_citations_is_untouched():
    answer = "Respuesta normal, sin fuentes."
    assert resolve_citations(answer, DOCS) == answer


def test_orphan_separator_is_cleaned_up():
    assert resolve_citations("Fin [F9].", DOCS) == "Fin."


def test_handles_an_empty_document_list():
    assert resolve_citations("Nada [F1].", []) == "Nada."
