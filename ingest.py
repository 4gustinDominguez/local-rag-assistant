import os

from db import add_document
from utils.pdf_ingest import process_pdf, split_text
from utils.text import sanitize_name

BASE_DIR = "subjects"


def ingest_uploaded_file(file, subject: str):
    subject_clean = sanitize_name(subject)

    subject_path = os.path.join(BASE_DIR, subject_clean)
    docs_path = os.path.join(subject_path, "docs")

    os.makedirs(docs_path, exist_ok=True)

    # Keep a copy of the original document
    pdf_path = os.path.join(docs_path, file.name)
    with open(pdf_path, "wb") as f:
        f.write(file.getbuffer())

    pages = process_pdf(pdf_path)

    for page_num, text in pages:
        for idx, chunk in enumerate(split_text(text)):
            add_document(
                subject_clean,
                f"{file.name}_p{page_num}_c{idx}",
                chunk,
                metadata={
                    "source": file.name,
                    "page": page_num,
                    "chunk": idx
                }
            )

    return file.name
