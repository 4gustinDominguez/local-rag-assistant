import re

from db import retrieve

# Citations emitted by the model: [F1], [F1][F4], [F2][F3]
_CITE = re.compile(r"\[F(\d+)\]")

# System context. There is no per-subject context: every subject shares
# this one, and the grounding rules below do the heavy lifting.
DEFAULT_CONTEXT = "Asistente general."


def resolve_citations(answer: str, docs: list) -> str:
    """Replace [Fn] with the real source.

    The model only picks a chunk number (so it cannot invent a page) and
    here that number is translated to the real document and page.
    Out-of-range citations are dropped instead of left broken.
    """
    def repl(match):
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(docs):
            meta = docs[idx].get("metadata", {}) or {}
            source = meta.get("source", "document")
            page = meta.get("page", "?")
            return f"[{source}, pág. {page}]"
        return ""

    resolved = _CITE.sub(repl, answer)
    # Drop orphan separators left behind by a removed citation
    # ("..., y  ." -> "..., y .")
    return re.sub(r"[,;:\s]*\s*\.", ".", resolved)


def build_prompt(question, docs, memory=None):
    history_block = ""
    if memory:
        history_block = "\n".join(
            [f"Usuario: {q}\nAsistente: {a}" for q, a in memory]
        )

    docs_block = "\n\n".join(
        f"[F{i}] {d['metadata']['source']}, pág. {d['metadata']['page']}\n"
        f"{d['text']}"
        for i, d in enumerate(docs, 1)
    )

    # Nothing retrieved means there is no material to answer from
    if not docs_block.strip():
        docs_block = "(sin documentos relevantes para esta pregunta)"

    return f"""
{DEFAULT_CONTEXT}

Historial reciente:
{history_block}

Contexto recuperado:
{docs_block}

INSTRUCCIONES OBLIGATORIAS:
- Responde basándote en el "Contexto recuperado". No uses conocimientos
  que no estén respaldados por él.
- Puedes sintetizar, resumir y derivar conclusiones a partir del contexto:
  no hace falta que la respuesta esté escrita de forma literal.
- Si el contexto desarrolla el tema de la pregunta, responde con normalidad,
  aunque lo haga en varias frases o cite varios fragmentos.
- Cita siempre las fuentes usando el identificador de fragmento tal y
  como aparece, por ejemplo [F2] o [F1][F4]. Nunca escribas el nombre
  del documento ni el número de página a mano.
- Comprueba antes de citar que el fragmento citado contiene de verdad
  lo que vas a afirmar. Si una afirmación se apoya en varios
  fragmentos, cita todos los relevantes.
- Si el contexto no trata el tema de la pregunta, o es claramente
  insuficiente para responder, responde exactamente:
  "No está en el material."
  y no añadas nada más.
- Nunca inventes fuentes, páginas ni contenido que no aparezca
  en el contexto recuperado.

Pregunta:
{question}

Respuesta clara y académica:
"""


def run_rag(question, subject, memory, cfg):
    docs = retrieve(
        subject,
        question,
        n=cfg["n_results"],
        max_distance=cfg["max_distance"]
    )

    docs = docs[:cfg["top_k"]]

    prompt = build_prompt(
        question,
        docs,
        memory
    )

    return prompt, docs
