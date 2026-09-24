# Reels Second Brain

Converts saved Instagram Reels into searchable notes.

## Pipeline

reels.json -> dedupe -> capture (tldw, CDP + transcribe in one)
-> extract (Gemini) -> store -> consolidate (Gemini, batched) -> markdown -> Obsidian

## Capture: tldw, not yt-dlp

Instagram capture goes through your own logged-in Chrome via Chrome
DevTools Protocol (CDP) — https://github.com/werg543/tldw. It opens the
reel in your real browser, captures the actual media stream Instagram
sends, and transcribes locally with faster-whisper. No login system, no
stored credentials, no cookie extraction.

Before running stage 2, start a Chrome instance yourself:

```
chrome --remote-debugging-port=9226 --user-data-dir="/path/to/a/profile"
```

Log into Instagram in that window. Leave it open. Point `.env` at your
cloned tldw repo (`TLDW_DIR`) and the CDP port (`TLDW_CDP`).

## Run order

```
python scripts/01_ingest.py      # load reels.json, update state.json
python scripts/02_capture.py     # tldw: video.mp4 + transcript.txt via CDP
python scripts/03_extract.py     # Gemini per-reel, extracted.json
python scripts/04_consolidate.py # Gemini batch, knowledge.json
python scripts/05_markdown.py    # notes/*.md
```

Each script only processes reels at the correct `state.json` stage. Safe to
re-run anytime — already-processed reels are skipped.

## Setup

```
git clone https://github.com/werg543/tldw   # separately, anywhere
cd tldw && npm install                       # provisions ffmpeg, whisper venv

pip install -r requirements.txt
cp .env.example .env   # fill in GEMINI_API_KEY, TLDW_DIR, TLDW_CDP
```

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

Rate limits: Instagram will wall you off if you capture too many reels
back to back. tldw tells you when this happens — slow down, let it recover.
