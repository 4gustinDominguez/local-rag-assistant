import re

import streamlit as st


def render_answer_with_latex(text: str):
    """Render the answer with Streamlit's standard Markdown.

    Streamlit renders LaTeX natively:
    - inline:  $...$
    - block:   $$...$$
    """
    st.markdown(text)


def autolatex(text: str) -> str:
    # \[ ... \]  ->  $$ ... $$
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)

    # \( ... \)  ->  $ ... $
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)

    # Bare [ ... ] that look like formulas (they contain \ or = and start
    # at the beginning of a line). Markdown links [text](url) are left
    # alone because they never sit on their own line like this.
    text = re.sub(
        r'(^|\n)\s*\[(.*?)\s*\](?=\s*(\n|$))',
        lambda m: (
            f"{m.group(1)}$${m.group(2)}$$"
            if ('\\' in m.group(2) or '=' in m.group(2)) else m.group(0)
        ),
        text,
        flags=re.DOTALL
    )

    return text
