"""LaTeX delimiter conversion."""
from utils.latex import autolatex


def test_bracket_delimiters_become_dollars():
    assert autolatex(r"\[ N = d_n \cdot b^n \]") == "$$ N = d_n \\cdot b^n $$"


def test_paren_delimiters_become_dollars():
    assert autolatex(r"\( E = mc^2 \)") == "$ E = mc^2 $"


def test_already_wrapped_input_is_untouched():
    assert autolatex("$$ E = mc^2 $$") == "$$ E = mc^2 $$"


def test_markdown_links_are_left_alone():
    source = "[docs](https://example.com)"
    assert autolatex(source) == source
