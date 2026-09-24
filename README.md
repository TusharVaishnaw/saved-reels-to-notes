# saved-reels-to-notes

Converts saved Instagram Reels into searchable markdown notes.

## Pipeline

```
reels.json -> dedupe -> capture (tldw, CDP + transcribe in one)
-> extract (Gemini) -> store -> consolidate (Gemini, batched) -> markdown -> Obsidian
```

## Capture: tldw, not yt-dlp

Instagram capture goes through your own logged-in Chrome via Chrome
DevTools Protocol (CDP) — https://github.com/werg543/tldw. It opens the
post in your real browser, captures the actual media stream Instagram
sends, and transcribes locally with faster-whisper. No login system, no
stored credentials, no cookie extraction.

Start a Chrome instance yourself before running stage 2:

```
chrome --remote-debugging-port=9226 --user-data-dir="C:\chrome-cdp-profile"
```

(If `chrome` isn't on PATH, use the full exe path — e.g.
`"C:\Program Files\Google\Chrome\Application\chrome.exe"`.)

Log into Instagram in that window. **Leave it open** for the entire time
you're running the pipeline — closing it kills the CDP session and
`02_capture.py` will fail with "Target page, context or browser has been
closed." If it closes, just relaunch with the same command and
`--user-data-dir` to stay logged in.

## Setup

```
git clone https://github.com/TusharVaishnaw/saved-reels-to-notes
cd saved-reels-to-notes

git clone https://github.com/werg543/tldw   # separate clone, own repo
cd tldw && npm install                       # provisions ffmpeg, whisper venv
cd ..

python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt

cp .env.example .env   # fill in GEMINI_API_KEY, TLDW_DIR (absolute path), TLDW_CDP
```

**Two separate venvs exist: this project's `.venv` and tldw's own
`tldw/.venv`.** Don't activate tldw's venv to run these scripts — it
won't have `google-genai`, `python-dotenv`, etc. Run
`$env:VIRTUAL_ENV` after activating to confirm you're in the right one
(should point at this project's `.venv`, not `tldw\.venv`).

`TLDW_DIR` in `.env` must be an **absolute path** to your tldw clone
(e.g. `C:/Users/you/saved-reels-to-notes/tldw`), not relative.

## Run order

```
python scripts/01_ingest.py path\to\reels.json   # load extension export, update state.json
python scripts/02_capture.py                     # tldw: video.mp4 + transcript.txt via CDP
python scripts/03_extract.py                     # Gemini per-reel, extracted.json
python scripts/04_consolidate.py                 # Gemini batch, knowledge.json
python scripts/05_markdown.py                    # notes/*.md
```

Each script only processes reels at the correct `state.json` stage. Safe to
re-run anytime — already-processed reels are skipped. On failure, check
`data/state.json` for a `stage_error` field on the failed entry.

## Models

Uses `gemini-3.5-flash-lite` for both extraction and consolidation
(swap in `scripts/03_extract.py` / `scripts/04_consolidate.py` if you have
access to a stronger model). Consolidation uses smaller chunks (10) and
iterative pairwise folding to compensate for a lite model's weaker
long-context deduplication.

## Data layout

```
data/
  state.json              # url -> {id, status, stage_error}
  reels/
    <id>/
      metadata.json       # from tldw's meta.json
      video.mp4           # only kept if KEEP_VIDEO=1
      transcript.txt
      extracted.json
  knowledge.json           # consolidated output
notes/
  <category>.md            # final markdown, Obsidian-ready
```

## Status flow

```
pending -> captured -> extracted -> consolidated
              |
           (tldw: CDP capture + faster-whisper transcribe, one call)
```

## Rate limits

Instagram will wall you off if you capture too many reels back to back.
tldw tells you when this happens in its terminal output — slow down and
let it recover rather than retrying immediately.

## Not tracked in git

`data/`, `notes/`, `.env`, `tldw/` (separate repo), and both `.venv/`
folders are gitignored. Clone tldw and create your own `.env` per Setup
above.
