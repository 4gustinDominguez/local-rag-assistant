"""Smoke test for the LaTeX delimiter conversion.

Run from the project root:  python -m tests.reproduce_latex
"""
from utils.latex import autolatex

CASES = [
    (
        "bracket delimiters [ ... ]",
        r"\[ N = d_n \cdot b^n \]",
        "$$ N = d_n \\cdot b^n $$",
    ),
    (
        "paren delimiters ( ... )",
        r"\( E = mc^2 \)",
        "$ E = mc^2 $",
    ),
    (
        "already dollar-wrapped is untouched",
        "$$ E = mc^2 $$",
        "$$ E = mc^2 $$",
    ),
    (
        "markdown link is left alone",
        "[docs](https://example.com)",
        "[docs](https://example.com)",
    ),
]


def test_autolatex():
    failures = []

    for name, source, expected in CASES:
        result = autolatex(source)
        if result != expected:
            failures.append((name, expected, result))

    return failures


if __name__ == "__main__":
    failures = test_autolatex()

    for name, expected, result in failures:
        print(f"FAIL: {name}")
        print(f"  expected: {expected!r}")
        print(f"  got:      {result!r}")

    passed = len(CASES) - len(failures)
    print(f"{passed}/{len(CASES)} passed")
    raise SystemExit(1 if failures else 0)
