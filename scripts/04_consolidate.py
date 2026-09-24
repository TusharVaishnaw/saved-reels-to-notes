"""
Batch-consolidate all extracted.json files with Gemini:
merge duplicate ideas/tools, group related ideas, attach source reel URLs,
never invent missing info. Chunked to respect context limits, then merged.
"""
import json
from google import genai

from config import REELS_DIR, KNOWLEDGE_FILE, GEMINI_API_KEY
from state import by_status, upsert

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.5-flash-lite"
CHUNK_SIZE = 10  # smaller chunks = fewer entities per call, less drift on a lite model

CONSOLIDATE_PROMPT = """You are consolidating extracted Reel notes into a \
canonical knowledge base.

Rules:
- Two entries are duplicates ONLY if they describe the same underlying idea, \
tool, or method — not just the same broad category.
- merge duplicate ideas and tools; keep genuinely distinct ideas separate
- group closely related ideas under one topic only when they share the same \
core concept
- preserve useful distinctions — do not merge two different tools just \
because they solve similar problems
- attach all relevant source reel URLs to each topic
- never invent information not present in the input
- if unsure whether two items are duplicates, keep them SEPARATE

Example:
Input topics: "AI invoice generator for freelancers", "automated invoice SaaS"
These ARE duplicates (same core idea) -> merge into one topic, both sources listed.

Input topics: "AI invoice generator", "AI receipt scanner"
These are NOT duplicates (different core idea) -> keep as two separate topics.

Input (list of {{url, extracted}} objects):
{items}

Return ONLY a JSON array of topics, each shaped like:
{{
  "topic": "...",
  "description": "...",
  "category": "...",
  "tools": [...],
  "steps_or_methods": [...],
  "tags": [...],
  "sources": ["url1", "url2"]
}}
"""

FOLD_PROMPT = """You are merging two lists of already-consolidated topics \
from a knowledge base into one canonical list.

Rules:
- Two topics are duplicates ONLY if they describe the same underlying idea, \
tool, or method — not just the same broad category.
- merge duplicate topics, combining their sources lists (no duplicate URLs)
- keep genuinely distinct topics separate — if unsure, keep them SEPARATE
- never invent information not present in the input

Topics to merge:
{items}

Return ONLY a JSON array of topics, same shape as the input (topic,
description, category, tools, steps_or_methods, tags, sources).
"""


def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def load_extracted_items():
    extracted = by_status("extracted", "consolidated")
    items = []
    for url, entry in extracted.items():
        path = REELS_DIR / entry["id"] / "extracted.json"
        if path.exists():
            items.append({"url": url, "extracted": json.loads(path.read_text())})
    return items


def consolidate_chunk(items):
    prompt = CONSOLIDATE_PROMPT.format(items=json.dumps(items, indent=2))
    resp = client.models.generate_content(model=MODEL, contents=prompt)
    raw = resp.text.strip().strip("```json").strip("```")
    return json.loads(raw)


def merge_final(chunk_results):
    """
    Fold chunk-level topic lists into one canonical set, two at a time.
    Iterative folding keeps each call's entity count small — more reliable
    on a lite model than dumping all chunks into one giant merge call.
    """
    if len(chunk_results) == 1:
        return chunk_results[0]

    acc = chunk_results[0]
    for next_chunk in chunk_results[1:]:
        combined = acc + next_chunk
        prompt = FOLD_PROMPT.format(items=json.dumps(combined, indent=2))
        resp = client.models.generate_content(model=MODEL, contents=prompt)
        raw = resp.text.strip().strip("```json").strip("```")
        acc = json.loads(raw)

    return acc


def main():
    items = load_extracted_items()
    if not items:
        print("nothing to consolidate")
        return

    chunk_results = [consolidate_chunk(c) for c in chunk(items, CHUNK_SIZE)]
    final = merge_final(chunk_results)

    KNOWLEDGE_FILE.write_text(json.dumps(final, indent=2))

    for item in items:
        upsert(item["url"], status="consolidated")

    print(f"consolidated {len(items)} reels into {len(final)} topics")


if __name__ == "__main__":
    main()