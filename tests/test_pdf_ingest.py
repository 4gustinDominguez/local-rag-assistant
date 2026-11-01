from utils.pdf_ingest import clean_page_text, split_text


# --- cleaning -----------------------------------------------------------

def test_recurring_header_is_removed():
    raw = ("CC-BY-SA • PID_00279130 39 Los circuitos lógicos combinacionales\n"
           "El texto real de la página.")
    assert clean_page_text(raw) == "El texto real de la página."


def test_table_of_contents_line_is_removed():
    raw = "2.2. Segunda generación (1955-1965) ............ 13\nContenido."
    assert clean_page_text(raw) == "Contenido."


def test_real_content_is_kept():
    assert "Karnaugh" in clean_page_text("El mapa de Karnaugh simplifica.")


def test_line_breaks_are_collapsed():
    assert clean_page_text("linea uno\nlinea dos") == "linea uno linea dos"


def test_blank_input_returns_empty_string():
    assert clean_page_text("   \n  ") == ""


# --- chunking -----------------------------------------------------------

SENTENCES = " ".join(f"Oracion numero {i}." for i in range(60))


def test_empty_text_produces_no_chunks():
    assert split_text("") == []
    assert split_text("   ") == []


def test_chunks_respect_the_size_limit():
    chunks = split_text(SENTENCES, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    assert max(len(c) for c in chunks) <= 200


def test_no_chunk_starts_or_ends_mid_sentence():
    """Cutting mid-word breaks semantic search."""
    chunks = split_text(SENTENCES, chunk_size=150, overlap=30)
    for chunk in chunks[:-1]:
        assert chunk.rstrip().endswith("."), f"bad cut: ...{chunk[-30:]!r}"


def test_no_text_is_lost():
    chunks = split_text(SENTENCES, chunk_size=150, overlap=30)
    for sentence in ("Oracion numero 0.", "Oracion numero 59."):
        assert any(sentence in c for c in chunks)


def test_overlap_keeps_context_from_the_previous_chunk():
    chunks = split_text(SENTENCES, chunk_size=120, overlap=40)
    assert len(chunks) >= 2

    # The last sentence of a chunk must reappear at the start of the next
    # one, otherwise each chunk would lose the context it was cut from.
    last_sentence = chunks[0].rstrip().rsplit(". ", 1)[-1]
    assert last_sentence in chunks[1]


def test_single_short_text_is_one_chunk():
    assert split_text("Texto corto.") == ["Texto corto."]
