"""
state.json = { canonical_url: { id, status, stage_error } }

status values, in order:
  pending      -> queued after ingest, not captured
  captured     -> video.mp4 + transcript.txt present (via tldw)
  extracted    -> extracted.json present
  consolidated -> included in latest knowledge.json
  failed       -> stage_error set, needs manual look
"""
import hashlib
import json
from config import STATE_FILE


def _load():
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text())


def _save(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def canonicalize(url: str) -> str:
    return url.split("?")[0].rstrip("/")


def reel_id(url: str) -> str:
    return hashlib.sha1(canonicalize(url).encode()).hexdigest()[:12]


def get_state():
    return _load()


def upsert(url: str, **fields):
    state = _load()
    url = canonicalize(url)
    entry = state.get(url, {"id": reel_id(url), "status": "pending"})
    entry.update(fields)
    state[url] = entry
    _save(state)
    return entry


def by_status(*statuses):
    state = _load()
    return {u: e for u, e in state.items() if e["status"] in statuses}


def mark_failed(url: str, error: str):
    upsert(url, status="failed", stage_error=str(error))
