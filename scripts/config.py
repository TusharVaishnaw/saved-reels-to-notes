"""Central paths + env. Import this everywhere. No logic here."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
REELS_DIR = DATA_DIR / "reels"
NOTES_DIR = ROOT / "notes"
STATE_FILE = DATA_DIR / "state.json"
KNOWLEDGE_FILE = DATA_DIR / "knowledge.json"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

TLDW_DIR = os.getenv("TLDW_DIR", "")  # path to cloned tldw repo
TLDW_CDP = os.getenv("TLDW_CDP", "http://localhost:9226")
KEEP_VIDEO = os.getenv("KEEP_VIDEO", "0") == "1"

DATA_DIR.mkdir(exist_ok=True)
REELS_DIR.mkdir(parents=True, exist_ok=True)
NOTES_DIR.mkdir(exist_ok=True)
