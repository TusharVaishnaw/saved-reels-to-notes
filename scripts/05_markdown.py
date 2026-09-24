"""
knowledge.json -> notes/<category>.md
One file per category, topics appended as sections. Obsidian-ready.
"""
import json
import re
from collections import defaultdict

from config import KNOWLEDGE_FILE, NOTES_DIR


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def render_topic(t: dict) -> str:
    lines = [f"## {t['topic']}", "", t.get("description", ""), ""]

    if t.get("tools"):
        lines += ["**Tools**", *[f"- {x}" for x in t["tools"]], ""]

    if t.get("steps_or_methods"):
        lines += ["**Method**", *[f"- {x}" for x in t["steps_or_methods"]], ""]

    if t.get("tags"):
        clean_tags = [re.sub(r"\s+", "-", tag.strip()) for tag in t["tags"]]
        lines += ["Tags: " + " ".join(f"#{tag}" for tag in clean_tags), ""]

    if t.get("sources"):
        lines += ["**Sources**", *[f"- {u}" for u in t["sources"]], ""]

    return "\n".join(lines)


def main():
    topics = json.loads(KNOWLEDGE_FILE.read_text())

    by_category = defaultdict(list)
    for t in topics:
        by_category[t.get("category", "uncategorized")].append(t)

    for category, items in by_category.items():
        path = NOTES_DIR / f"{slugify(category)}.md"
        body = "\n---\n\n".join(render_topic(t) for t in items)
        path.write_text(f"# {category}\n\n{body}\n")

    print(f"wrote {len(by_category)} note files to {NOTES_DIR}")


if __name__ == "__main__":
    main()