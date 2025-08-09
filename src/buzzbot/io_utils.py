import json
from pathlib import Path
from typing import Iterable, List, Dict, Any
import datetime as _dt
import sys

Message = Dict[str, Any]

SESSIONS_DIR = Path("data/sessions")


def ensure_sessions_dir():
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def timestamp() -> str:
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat().replace(":", "-")


def save_history(history: List[Message]) -> Path:
    ensure_sessions_dir()
    path = SESSIONS_DIR / f"{timestamp()}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for msg in history:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    return path


def load_history(path: Path) -> List[Message]:
    loaded: List[Message] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                loaded.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line in {path}", file=sys.stderr)
    return loaded

# Formatting utilities -------------------------------------------------------
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"


def colorize(text: str, color_code: str, enable: bool) -> str:
    if not enable:
        return text
    return f"{color_code}{text}{RESET}"


def format_prefix(role: str, color: bool) -> str:
    if role == "user":
        return colorize("you:", GREEN, color)
    if role == "assistant":
        return colorize("assistant:", CYAN, color)
    if role == "system":
        return colorize("system:", YELLOW, color)
    return f"{role}:"


def print_message(msg: Message, color: bool, stream: bool = False):
    prefix = format_prefix(msg.get("role", "?"), color)
    content = msg.get("content", "")
    if stream:
        # streaming prints are handled token-by-token elsewhere
        return
    print(f"{prefix} {content}")

