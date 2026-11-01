import re
from PyPDF2 import PdfReader

# Recurring page header/footer of the PDF. It repeats on every page, so
# leaving it in pollutes the index (it would appear in every chunk).
_HEADER = re.compile(
    r"^\s*(?:CC-BY-SA\s*[•·]\s*PID_\d+|PID_\d+)\s*\d*\s*"
    r"(?:[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ .,'-]{0,60})?",
    re.M,
)

# Table-of-contents line ("2.2. Second generation ..... 13"). It is a map
# of the document, not content: it adds no knowledge and competes in the
# semantic search because it mentions every topic at once.
_INDEX_LINE = re.compile(r"^.{0,120}[.·…]{4,}\s*\d+\s*$")


def clean_page_text(text: str) -> str:
    """Strip recurring headers and indexes, normalise line breaks."""
    text = _HEADER.sub("", text)
    text = "\n".join(line for line in text.split("\n")
                     if not _INDEX_LINE.match(line))
    # Collapse the PDF's internal line breaks: they are not real paragraphs
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    return text.strip()


def split_text(text: str, chunk_size=1000, overlap=150):
    """Split into chunks, always cutting on a line or sentence boundary.

    PyPDF2 output has almost no blank lines (so splitting on paragraphs
    does not work), but it does have line breaks. Cutting mid-word breaks
    semantic search, so lines are grouped whole until chunk_size.
    """
    text = clean_page_text(text)
    if not text:
        return []

    units = re.split(r"(?<=[.!?¿])\s+|\s*\n\s*", text)

    chunks = []
    current = ""

    for unit in units:
        unit = unit.strip()
        if not unit:
            continue

        candidate = f"{current} {unit}".strip()

        # Normal cut: the piece is already large enough
        if len(candidate) >= chunk_size and current:
            chunks.append(current)
            # Overlap: keep the tail of the previous chunk
            tail = current[-overlap:]
            cut = max(tail.find(". "), tail.find("\n"))
            current = (tail[cut + 1:] if cut >= 0 else tail).strip()
            current = f"{current} {unit}".strip()
        else:
            current = candidate

    if current.strip():
        chunks.append(current.strip())

    return chunks


def process_pdf(file):
    reader = PdfReader(file)
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append((i + 1, text))

    return pages
