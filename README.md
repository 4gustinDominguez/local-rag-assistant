# Local RAG Assistant for University Studies (Telecommunications)

A **Retrieval-Augmented Generation (RAG) assistant** built to support
**university-level study**, aimed at Telecommunications Engineering
coursework.

It is not a demo chatbot. It is a practical academic tool intended to:

- ingest real study material (PDFs)
- retrieve relevant fragments
- answer questions with traceable sources
- refuse to answer when the material does not cover the question
- behave like a study tutor

It runs on **Ollama** for generation (local or cloud) and **ChromaDB +
sentence-transformers** for retrieval, with a **Streamlit** interface.

---

## Core Goals

- Support multiple subjects (courses) and multiple documents per subject
- Handle large PDFs (100+ pages)
- Answer questions with academic rigor and real source attribution
- Say **"No está en el material."** instead of answering from general
  knowledge when nothing relevant is retrieved
- Support mathematical notation (LaTeX)
- Keep short conversational context

---

## Quickstart

```bash
make setup          # creates venv with uv and installs dependencies
make run            # starts the Streamlit app
```

You also need Ollama with at least one generation model:

```bash
ollama pull llama3.2:latest
ollama list
```

Optional: for the cloud model, create an API key at
<https://ollama.com/settings/keys> and put it in `.env`:

```bash
OLLAMA_API_KEY=your_key_here
```

`.env` is git-ignored. Never commit it.

```bash
make test           # unit tests (pytest, no network or models needed)
make lint           # flake8
make help           # lists all targets
```

---

## Models

The model picker mixes **local** and **cloud** models and the code routes
each request automatically (`llm.is_cloud_model`):

| Model | Where it runs | Notes |
|---|---|---|
| `llama3.2:latest` | local, 2.0 GB | default; ~26 tok/s on CPU |
| `qwen2.5:7b` | local, 4.7 GB | slower on CPU (~13 tok/s) |
| `gemma4:31b-cloud` | Ollama cloud | needs `OLLAMA_API_KEY`; ~1 s |

Local models keep everything on the machine. Cloud models send the
retrieved context to `ollama.com` — see *Limitations*.

---

## Architecture

### 1. Frontend — `app.py`

Streamlit application. Lets you create subjects, upload PDFs, ask
questions, view ranked sources, and browse saved chats.

### 2. Subjects (courses)

```
subjects/
  fundamentos-de-computadores/
    docs/     # original PDFs
    db/       # persistent ChromaDB index
  matematicas/
```

Each subject has its own collection, so context never bleeds between
courses.

### 3. Document ingestion — `ingest.py`, `utils/pdf_ingest.py`

Each PDF is parsed, cleaned, split into chunks, embedded and stored in
ChromaDB. Every chunk carries `source`, `page` and `chunk` metadata for
precise attribution.

The cleaning step is automatic and document-agnostic — no manual page
filtering:

- strips the recurring page header (`CC-BY-SA • PID_…`)
- strips table-of-contents lines (`2.2. Section ..... 13`), which compete
  in semantic search while adding no knowledge
- collapses the PDF's internal line breaks
- **splits on line/sentence boundaries**, never mid-word. PyPDF2 output
  has almost no blank lines, so paragraph-based splitting does not work.

### 4. Vector database — `db.py`

- `PersistentClient`, one collection per subject, cosine distance
- embedder: **`intfloat/multilingual-e5-large`** (1024 dims), applied
  consistently at ingestion and query time
- retrieval returns chunk text, metadata and distance

Measured on this corpus, switching from `all-MiniLM-L6-v2` to
`multilingual-e5-large` improved `recall@6` from **43% to 86%** and the
median rank of the correct chunk from **10.3 to 2.7**.

> Changing the embedding model requires re-ingesting the corpus **and**
> recalibrating `max_distance` (see below).

### 5. Relevance threshold

`retrieve()` discards chunks whose cosine distance exceeds
`max_distance` (default **0.19**, calibrated for `multilingual-e5-large`:
relevant ≤ 0.18, irrelevant ≥ 0.21).

If **nothing** passes the threshold, the prompt says there is no material
and the model must answer literally *"No está en el material."* — so
refusal is deterministic, not a model judgement call.

### 6. RAG pipeline — `rag.py`

Retrieves chunks, trims to `top_k`, and builds a structured prompt with:

- subject-specific system context
- short conversation history
- retrieved fragments, labelled `[F1] [F2] …`
- the current question

**Grounding rules** in the prompt require the model to answer only from
the retrieved context, to synthesise rather than copy verbatim, and to
refuse when the context does not cover the topic.

**Citations** are resolved programmatically: the model only emits a
fragment id (`[F3]`) and `resolve_citations()` maps it to the real
document and page. The model therefore cannot invent a source.

### 7. Short-term memory — `memory.py`

Last N turns per subject, held in `streamlit.session_state`. Session-only
and temporary.

### 8. Chat history — `chat_store.py`

Every turn is appended to `chats/<subject>/<date>.md` with question,
answer, sources and scores. Browsable from the UI.

### 9. Math rendering — `utils/latex.py`

LaTeX delimiters are normalised and rendered through Streamlit's native
Markdown support.

### 10. Performance

The sidebar exposes `temperature`, `max_tokens`, `n_results`, `top_k` and
`max_distance`. `max_tokens` matters a lot on CPU: without it the model
generated 600–750 tokens per answer and a query took ~40 s; capped at 400
it drops to ~15 s.

---

## Project structure

```
app.py                 Streamlit entry point
rag.py                 prompt building + citation resolution
llm.py                 local/cloud routing via Ollama
db.py                  ChromaDB access, embeddings, relevance filtering
ingest.py              document ingestion
chat_store.py          chat history persistence
memory.py              short-term session memory
subjects_manager.py    subject creation and listing
config/rag_defaults.py prompts and default RAG parameters
core/logging.py        rotating file logger
ui/rag_sidebar.py      configuration sidebar
ui/metrics.py          latency metrics
utils/pdf_ingest.py    PDF parsing, cleaning and chunking
utils/latex.py         LaTeX normalisation and rendering
utils/text.py          name sanitisation
tests/                 unit tests (pytest)
conftest.py            makes the project root importable for pytest
```

---

## Testing

```bash
make test      # 45 unit tests, ~0.6 s
make lint      # flake8
```

The tests cover the parts that fail silently if they break, and none of
them need a model, a network call or a database:

- **`utils/pdf_ingest`** — header and index removal, and that chunks are
  never cut mid-sentence and never lose text. Bad chunking degrades
  retrieval without raising any error.
- **`rag.resolve_citations`** — that `[Fn]` maps to a real source, and
  that an out-of-range id is dropped rather than left broken.
- **`llm.is_cloud_model`** — local/cloud routing.
- **`rag.build_prompt`** — that the grounding rules and the
  "no relevant documents" branch are actually present.
- **`utils.text.sanitize_name`** — including a regression test for
  accents: `Matemáticas` used to become `matemticas`, which silently
  created a second, empty subject folder.
- **`utils.latex`** — LaTeX delimiter conversion.

## What works

- Multiple subjects, multiple PDFs per subject, large real documents
- Automatic document cleaning and boundary-aware chunking
- Persistent vector storage with a multilingual embedding model
- Relevance filtering with a calibrated threshold
- Deterministic refusal when nothing relevant is retrieved
- Source attribution (document, page, distance) resolved in code
- LaTeX rendering, short conversational memory, saved chat history
- Local and cloud models behind a single selector

---

## Limitations

Be aware of these; they are measured, not hypothetical.

- **CPU latency.** Without a GPU, generation runs at ~22 tok/s.
  `llama3.2` answers in roughly 10–30 s; the cloud model in ~1 s.
- **Citation precision is model-dependent.** Citations always point to a
  real retrieved chunk, but the model does not always pick the chunk that
  best supports the claim: `gemma4` tends to over-cite, while `llama3.2`
  sometimes omits citations entirely.
- **One known retrieval miss.** For *"¿Qué es un circuito combinacional?"*
  the formal definition (page 5) falls outside `top_k` because it is
  diluted inside a longer introduction chunk. All five embedding models
  tested showed the same behaviour — this is a chunk-granularity issue,
  not an embedding issue.
- **Cloud models break the offline promise.** Sending a question to
  `gemma4:31b-cloud` transmits the retrieved document excerpts to
  `ollama.com`. Use a local model when the material must stay private.
- **The relevance threshold is model-specific.** It is calibrated for
  `multilingual-e5-large` and will misbehave if you swap the embedder.

---

## Intended next steps

- Re-ranking of retrieved candidates before prompting
- Smaller chunks so short definitions are not diluted
- Export of answers and sources to PDF
- Exam-focused prompt modes

---

## Summary

A working, measured RAG system for real university study: automatic
indexing, calibrated retrieval, deterministic refusal, and traceable
sources — running locally, with an optional cloud model.
