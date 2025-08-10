import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

# Extensibility: Add additional provider-specific settings here later.

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
APP_SAVING_DIR = Path("data") # Where to store app data, like session history, generated videos, etc.

DOT_ENV_PATH = Path('env/.env')
# Minimal .env loader (no external dependency) ---------------------------------
# Loads lines of form KEY=VALUE ignoring comments / blanks. Does not overwrite
# existing environment variables.
_DEF_ENV_LOADED = False

def _load_dotenv_once():
    global _DEF_ENV_LOADED
    if _DEF_ENV_LOADED:
        return
    env_path = DOT_ENV_PATH
    if env_path.exists():
        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            # remove potential surrounding quotes
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)
    _DEF_ENV_LOADED = True


@dataclass
class AppConfig:
    openai_api_key: str
    google_api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    system_prompt: Optional[str] = None
    color: bool = True
    debug: bool = False

    @classmethod
    def load(cls) -> "AppConfig":
        _load_dotenv_once()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise RuntimeError("Missing OPENAI_API_KEY environment variable.")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise RuntimeError("Missing GOOGLE_API_KEY environment variable.")
        base_url = os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        system_prompt = os.getenv("OPENAI_SYSTEM_PROMPT")  # optional
        no_color = os.getenv("NO_COLOR") or os.getenv("BUZZBOT_NO_COLOR")
        color = not bool(no_color)
        
        # Check for debug mode
        debug_env = os.getenv("DEBUG") or os.getenv("BUZZBOT_DEBUG")
        debug = str(debug_env).lower() in ("1", "true", "yes", "on")
        global DEBUG
        DEBUG = debug
        print(f"NB: DEBUG mode is {'enabled' if debug else 'disabled'}.")
        
        return cls(
            openai_api_key=openai_api_key,
            google_api_key=google_api_key,
            base_url=base_url,
            model=model,
            system_prompt=system_prompt,
            color=color,
            debug=debug
        )

    def switch_model(self, new_model: str):
        self.model = new_model

