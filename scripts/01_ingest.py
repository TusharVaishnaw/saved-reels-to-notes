"""
Load reels.json (exported from the Chrome extension).
Add new URLs to state.json as 'pending'. Skip URLs already known.
Usage: python 01_ingest.py path/to/reels.json
"""
import json
import sys
from state import upsert, canonicalize, get_state


def main(json_path: str):
    data = json.loads(open(json_path).read())
    urls = [r["url"] for r in data.get("reels", [])]

    known = get_state()
    added, skipped = 0, 0

    for url in urls:
        c = canonicalize(url)
        if c in known:
            skipped += 1
            continue
        upsert(c, status="pending")
        added += 1

    print(f"added={added} skipped_existing={skipped} total_in_file={len(urls)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python 01_ingest.py path/to/reels.json")
        sys.exit(1)
    main(sys.argv[1])
