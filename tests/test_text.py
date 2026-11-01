from utils.text import sanitize_name


def test_lowercases_and_trims():
    assert sanitize_name("  Telecom  ") == "telecom"


def test_spaces_become_dashes():
    assert sanitize_name("Fundamentos de Computadores") == (
        "fundamentos-de-computadores"
    )


def test_accents_are_folded_not_dropped():
    """Regression: accents used to be stripped, so "Matemáticas" became
    "matemticas" and the subject split into a second, empty folder."""
    assert sanitize_name("Matemáticas") == "matematicas"


def test_name_is_the_same_whether_typed_with_or_without_accents():
    assert sanitize_name("Matemáticas") == sanitize_name("matematicas")
    assert sanitize_name("Señales") == sanitize_name("senales")


def test_existing_subjects_are_unaffected():
    for name in ("fundamentos-de-computadores", "matematicas"):
        assert sanitize_name(name) == name


def test_short_names_get_a_suffix():
    assert sanitize_name("ab") == "ab001"


def test_punctuation_is_removed():
    assert sanitize_name("ÑOÑO!!") == "nono"


def test_output_is_always_a_safe_folder_name():
    for raw in ("Matemáticas", "a b c", "¿Qué es?", "señales & sistemas"):
        clean = sanitize_name(raw)
        assert clean
        assert clean == clean.lower()
        assert not any(c in clean for c in ' \\/*?:"<>|')
