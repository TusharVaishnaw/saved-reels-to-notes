"""
Send each transcript to Gemini with the extraction schema.
Saves extracted.json per reel. One Gemini call per reel.
"""
import json
from google import genai
from tqdm import tqdm

from config import REELS_DIR, GEMINI_API_KEY
from state import by_status, upsert, mark_failed
from schema import EXTRACTION_SCHEMA, EXTRACTION_PROMPT

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.5-flash-lite"


def extract_one(rid: str):
    reel_dir = REELS_DIR / rid
    transcript = (reel_dir / "transcript.txt").read_text()
    meta_path = reel_dir / "metadata.json"
    caption = ""
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        caption = meta.get("description", "") or meta.get("caption", "")

    prompt = EXTRACTION_PROMPT.format(
        schema=json.dumps(EXTRACTION_SCHEMA, indent=2),
        transcript=transcript,
        caption=caption,
    )

    resp = client.models.generate_content(model=MODEL, contents=prompt)
    raw = resp.text.strip().strip("```json").strip("```")
    extracted = json.loads(raw)

    (reel_dir / "extracted.json").write_text(json.dumps(extracted, indent=2))
    return extracted


def main():
    captured = by_status("captured")
    for url, entry in tqdm(captured.items(), desc="extracting"):
        rid = entry["id"]
        try:
            extract_one(rid)
            upsert(url, status="extracted")
        except Exception as e:
            print(f"FAILED {url}: {e}")
            mark_failed(url, e)


if __name__ == "__main__":
    main()