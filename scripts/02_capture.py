"""
Capture each 'pending' reel using tldw (CDP capture through your own
logged-in browser, no login/cookies/yt-dlp for Instagram).

Requires: a Chrome instance already running with remote debugging on,
logged into Instagram, matching TLDW_CDP in .env:

    chrome --remote-debugging-port=9226 --user-data-dir="/path/to/profile"

tldw writes video.mp4, audio.wav, transcript.txt, frames/, meta.json into
its own --out dir. This script runs it, then copies/normalizes those into
our data/reels/<id>/ layout and updates state.json.
"""
import json
import shutil
import subprocess
from pathlib import Path

from config import REELS_DIR, TLDW_DIR, TLDW_CDP, WHISPER_MODEL, KEEP_VIDEO
from state import by_status, upsert, mark_failed
from tqdm import tqdm


def run_tldw(url: str, out_dir: Path):
    if not TLDW_DIR:
        raise RuntimeError("TLDW_DIR not set in .env — point it at your cloned tldw repo")

    cmd = [
        "node", str(Path(TLDW_DIR) / "tldw.mjs"),
        url,
        "--out", str(out_dir),
        "--cdp", TLDW_CDP,
        "--model", WHISPER_MODEL,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=TLDW_DIR)


def normalize(out_dir: Path, reel_dir: Path):
    """tldw's output folder -> our data/reels/<id>/ layout."""
    reel_dir.mkdir(parents=True, exist_ok=True)

    src_meta = out_dir / "meta.json"
    src_transcript = out_dir / "transcript.txt"
    src_video = out_dir / "video.mp4"

    if src_meta.exists():
        shutil.copy(src_meta, reel_dir / "metadata.json")
    if src_transcript.exists():
        shutil.copy(src_transcript, reel_dir / "transcript.txt")
    else:
        raise RuntimeError("tldw did not produce transcript.txt")

    if src_video.exists():
        if KEEP_VIDEO:
            shutil.copy(src_video, reel_dir / "video.mp4")
    # frames/ intentionally not copied — not used downstream


def capture_one(url: str, rid: str):
    out_dir = REELS_DIR / rid / "_tldw_raw"
    reel_dir = REELS_DIR / rid

    run_tldw(url, out_dir)
    normalize(out_dir, reel_dir)
    shutil.rmtree(out_dir, ignore_errors=True)


def main():
    pending = by_status("pending")
    for url, entry in tqdm(pending.items(), desc="capturing"):
        rid = entry["id"]
        try:
            capture_one(url, rid)
            upsert(url, status="captured")
        except Exception as e:
            mark_failed(url, e)


if __name__ == "__main__":
    main()
