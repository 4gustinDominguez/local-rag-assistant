import os
from datetime import date

BASE_DIR = "chats"


def list_chat_dates(subject):
    subject_dir = os.path.join(BASE_DIR, subject)
    if not os.path.exists(subject_dir):
        return []

    files = [
        f.replace(".md", "")
        for f in os.listdir(subject_dir)
        if f.endswith(".md")
    ]
    return sorted(files, reverse=True)


def load_chat(subject, date_str):
    path = os.path.join(BASE_DIR, subject, f"{date_str}.md")
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_turn(subject, question, answer, docs):
    today = date.today().isoformat()

    subject_dir = os.path.join(BASE_DIR, subject)
    os.makedirs(subject_dir, exist_ok=True)

    path = os.path.join(subject_dir, f"{today}.md")

    q_number = 1
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            q_number = f.read().count("## Q") + 1

    with open(path, "a", encoding="utf-8") as f:
        if q_number == 1:
            f.write(f"# Chat – {subject.capitalize()}\n")
            f.write(f"Date: {today}\n\n---\n\n")

        f.write(f"## Q{q_number}\n")
        f.write("**Question:**\n")
        f.write(f"{question}\n\n")

        f.write("**Answer:**\n")
        f.write(f"{answer}\n\n")

        if docs:
            f.write("**Sources:**\n")
            for d in docs:
                meta = d.get("metadata", {})
                score = d.get("score", None)

                src = meta.get("source", "unknown")
                page = meta.get("page", "?")

                line = f"- {src} – page {page}"
                if score is not None:
                    line += f" (score {score:.2f})"

                f.write(line + "\n")

        f.write("\n---\n\n")
