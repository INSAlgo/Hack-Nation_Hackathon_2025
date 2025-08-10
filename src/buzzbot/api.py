"""Flask implementation of the BuzzBot Web Server (API layer).

Replaces the previous Starlette/Uvicorn server so that the CLI `--webserver` mode
now runs a Flask app. Endpoints are the same for compatibility.

Run (dev):
    PYTHONPATH=src python3 src/main.py --webserver --webserver-port 8000 --webserver-reload
"""
from __future__ import annotations

import uuid
import threading
from typing import Dict, List, Optional, Any

from flask import Flask, request, jsonify, send_from_directory, render_template

from .config import AppConfig
from .chat import ChatSession
from .io_utils import save_history
from .veo3 import generate_veo3_video

from pathlib import Path as _Path
BASE_DIR = _Path(__file__).resolve().parent
WEBUI_DIR = BASE_DIR / 'webui'
WEBUI_DIST_DIR = WEBUI_DIR / 'dist'
WEBUI_INDEX = WEBUI_DIST_DIR / 'index.html'

# Serve static files from the built frontend (assume Vite/React build output in 'dist')
app = Flask(
    __name__,
    static_folder=str(WEBUI_DIST_DIR),
    static_url_path=''
)

"""
This file has moved. See buzzbot/webserver.py for the Flask web server implementation.
"""
_locks: Dict[str, threading.Lock] = {}
