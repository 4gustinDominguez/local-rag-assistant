# Project instructions

Local RAG study assistant. Streamlit frontend, ChromaDB + sentence-transformers
for retrieval, Ollama for generation (local models or the cloud API).

## Commands

```bash
make setup   # create venv with uv and install dependencies
make run     # start the app
make test    # unit tests (pytest, ~0.6 s, no network or models needed)
make lint    # flake8
```

**Run `make lint` and `make test` before considering any change done.**
Both must pass. The tests cover the parts that fail silently if broken.

## Constraints that break silently

These are the rules most likely to be violated without an obvious error.

- **`max_distance` is calibrated for `intfloat/multilingual-e5-large`.**
  Relevant chunks score <= 0.18, irrelevant ones >= 0.21. If the embedding
  model changes, recalibrate it: measure distances for questions that are in
  the corpus and for questions that are not, then set the threshold in the
  gap between them. A wrong value makes `retrieve()` return garbage or
  nothing, and the refusal rule below stops working correctly.
- **Changing the embedding model requires a clean re-ingest.** A collection
  is bound to one model's vector size. Delete `subjects/<name>/db` and
  re-upload the documents through the app; never mix vectors from two models
  in the same collection.
- **Chunks must never be cut mid-sentence.** `utils/pdf_ingest.py` groups
  whole lines/sentences on purpose. Cutting by fixed character count
  damages semantic search without raising any error.
- **Page headers and table-of-contents lines are stripped during ingest.**
  They repeat on every page and compete in semantic search while adding no
  knowledge. Keep `clean_page_text()` in sync if the document format changes.
- **Never commit** `.env`, `subjects/*/docs/*.pdf`, `subjects/*/db/`,
  `chats/` or `logs/`. `.gitignore` already covers them — do not weaken it.

## Design decisions

- **Citations are resolved in code, not by the model.** The prompt asks for
  fragment ids (`[F1]`, `[F2]`) and `resolve_citations()` maps them to the
  real document and page. Do not ask the model to write page numbers: it
  invents them.
- **Refusal must stay deterministic.** When `retrieve()` returns nothing,
  the prompt contains no material and the model must answer
  `"No está en el material."`. This is what keeps the assistant from
  answering from general knowledge. Do not soften that instruction.
- **Local vs cloud routing is name-based.** `llm.is_cloud_model()` sends
  `-cloud` suffixed models to `https://ollama.com` with `OLLAMA_API_KEY`
  from `.env`, everything else to `localhost:11434`. Adding a cloud model
  means no code change, only a name ending in `-cloud`.
- **`max_tokens` matters on CPU.** Without it the model generates 600–750
  tokens per answer and a query takes ~40 s. The default of 400 keeps it
  around 15 s.

## Layout

- `app.py` — Streamlit entry point; wiring only, no business logic
- `rag.py` — prompt building and citation resolution
- `llm.py` — Ollama client and local/cloud routing
- `db.py` — ChromaDB access, embeddings, relevance filtering
- `utils/pdf_ingest.py` — PDF parsing, cleaning, chunking
- `config/rag_defaults.py` — prompts and default RAG parameters
