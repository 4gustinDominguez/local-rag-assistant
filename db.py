import os

import chromadb
from chromadb.utils import embedding_functions

from utils.text import sanitize_name


def get_client(subject):
    db_path = f"subjects/{subject}/db"
    os.makedirs(db_path, exist_ok=True)
    return chromadb.PersistentClient(path=db_path)


def get_embedder():
    # Multilingual: on technical Spanish it performs much better than
    # all-MiniLM-L6-v2 (recall@6: 86% vs 43%). Used without the
    # query:/passage: prefixes - measured, it scores the same and avoids
    # custom code. Changing this model requires re-ingesting the corpus.
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="intfloat/multilingual-e5-large"
    )


def get_collection(subject):
    subject = sanitize_name(subject)
    client = get_client(subject)

    try:
        col = client.get_collection(subject)
    except chromadb.errors.NotFoundError:
        col = client.create_collection(
            name=subject,
            metadata={"hnsw:space": "cosine"},
        )

    # Re-attach the embedder even when the collection already exists,
    # otherwise Chroma falls back to its default embedding function.
    col._embedding_function = get_embedder()

    return col


def add_document(subject, doc_id, text, metadata=None):
    col = get_collection(subject)
    col.add(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata or {}]
    )


def retrieve(subject, query, n=5, max_distance=None):
    """Retrieve the n most relevant chunks.

    max_distance is the relevance threshold (cosine distance): chunks
    farther away than this are discarded. If nothing passes the
    threshold an empty list is returned and the RAG answers
    'No está en el material'.
    """
    col = get_collection(subject)

    res = col.query(
        query_texts=[query],
        n_results=n
    )

    docs = []

    documents = res.get("documents", [[]])[0]
    metadatas = res.get("metadatas", [[]])[0]
    distances = res.get("distances", [[]])[0]

    for text, meta, dist in zip(documents, metadatas, distances):
        if max_distance is not None and dist > max_distance:
            continue

        docs.append({
            "text": text,
            "metadata": meta or {},
            "score": float(dist)
        })

    # Sort by score (lower is better)
    docs.sort(key=lambda d: d["score"])

    return docs
