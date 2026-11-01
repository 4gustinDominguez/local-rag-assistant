import re
import unicodedata


def sanitize_name(name: str) -> str:
    """Turn an arbitrary name into a safe folder name.

    Accents are folded rather than dropped, so "Matemáticas" becomes
    "matematicas" instead of "matemticas" — otherwise the same subject
    would split into two different folders depending on how it is typed.
    """
    name = name.lower().strip()

    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))

    name = re.sub(r"\s+", "-", name)

    name = re.sub(r"[^a-z0-9._-]", "", name)

    if len(name) < 3:
        name = name + "001"

    return name
