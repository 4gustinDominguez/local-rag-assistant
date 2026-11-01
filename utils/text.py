import re


def sanitize_name(name: str) -> str:
    name = name.lower().strip()

    name = re.sub(r"\s+", "-", name)

    name = re.sub(r"[^a-z0-9._-]", "", name)

    if len(name) < 3:
        name = name + "001"

    return name
