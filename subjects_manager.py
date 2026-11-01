import os

from utils.text import sanitize_name

BASE_PATH = "subjects"


def create_subject(name: str):
    clean = sanitize_name(name)
    subject_path = os.path.join(BASE_PATH, clean)

    os.makedirs(subject_path, exist_ok=True)
    os.makedirs(os.path.join(subject_path, "docs"), exist_ok=True)
    os.makedirs(os.path.join(subject_path, "db"), exist_ok=True)

    return clean


def list_documents(subject: str) -> list[str]:
    """
    Devuelve la lista de archivos (PDF/TXT) que existen en la carpeta 'docs'
    de la asignatura dada.
    """
    subject_clean = sanitize_name(subject)
    docs_path = os.path.join(BASE_PATH, subject_clean, "docs")

    if not os.path.isdir(docs_path):
        return []

    return sorted(os.listdir(docs_path))
