
from __future__ import annotations
# --- Error logging: log full stack trace to console on errors ---
import logging
import traceback
from flask import got_request_exception

"""Flask implementation of the BuzzBot Web Server (API layer).

Replaces the previous Starlette/Uvicorn server so that the CLI `--webserver` mode
now runs a Flask app. Endpoints are the same for compatibility.

Run (dev):
    PYTHONPATH=src python3 src/main.py --webserver --webserver-port 8000 --webserver-reload
"""

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

# --- Error logging: log full stack trace to console on errors ---
import logging
import traceback

@app.errorhandler(Exception)
def handle_exception(e):
    # Log full traceback to console
    logging.error("Exception on request: %s", request.path)
    traceback.print_exc()
    # Return JSON error
    return jsonify({"error": str(e), "type": type(e).__name__}), getattr(e, "code", 500)

# Global config + session store -------------------------------------------------
_config = AppConfig.load()
_sessions: Dict[str, ChatSession] = {}
_locks: Dict[str, threading.Lock] = {}
_global_lock = threading.Lock()


def _create_session(model: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
    cfg = _config
    model_to_use = model or cfg.model
    new_cfg = type(cfg)(
        openai_api_key=cfg.openai_api_key,
        google_api_key=cfg.google_api_key,
        base_url=cfg.base_url,
        model=model_to_use,
        system_prompt=system_prompt or cfg.system_prompt,
        color=False,
        debug=cfg.debug,
    )
    session = ChatSession(config=new_cfg)
    sid = uuid.uuid4().hex
    _sessions[sid] = session
    _locks[sid] = threading.Lock()
    return sid


def _ensure_base_session():
    if not _sessions:
        _create_session()


def _session_payload(session_id: str):
    s = _sessions[session_id]
    return {
        "session_id": session_id,
        "model": s.config.model,
        "system_prompt": s.config.system_prompt,
        "messages": len(s.history),
    }


## CORS (simple) ----------------------------------------------------------------
@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "*"
    return resp


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# Serve index.html for root and all unknown routes (SPA fallback)
@app.route("/")
@app.route("/<path:path>")
def serve_frontend(path=None):
    if path and (WEBUI_DIST_DIR / path).exists():
        return send_from_directory(str(WEBUI_DIST_DIR), path)
    return send_from_directory(str(WEBUI_DIST_DIR), "index.html")


@app.route("/session/new", methods=["POST"])
def session_new():
    data = request.get_json(force=True) or {}
    sid = _create_session(model=data.get("model"), system_prompt=data.get("system_prompt"))
    return jsonify(_session_payload(sid))


@app.route("/session/<session_id>", methods=["GET"])
def get_session(session_id: str):
    if session_id not in _sessions:
        return jsonify({"error": "not_found"}), 404
    payload = _session_payload(session_id)
    payload["history"] = _sessions[session_id].history
    return jsonify(payload)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "missing prompt"}), 400
    sid = data.get("session_id")
    if not sid or sid not in _sessions:
        sid = _create_session(model=data.get("model"))
    session = _sessions[sid]
    lock = _locks[sid]
    with lock:
        if data.get("model") and data.get("model") != session.config.model:
            session.switch_model(data.get("model"))
        if data.get("reset"):
            session.history.clear()
            if session.config.system_prompt:
                session.history.append({"role": "system", "content": session.config.system_prompt})
        reply_msg = session.complete(prompt)
        return jsonify({
            "session_id": sid,
            "reply": reply_msg.get("content", ""),
            "model": session.config.model,
            "history": session.history,
        })


@app.route("/session/<session_id>/model", methods=["POST"])
def switch_model(session_id: str):
    if session_id not in _sessions:
        return jsonify({"error": "not_found"}), 404
    data = request.get_json(force=True) or {}
    model = data.get("model")
    if not model:
        return jsonify({"error": "missing model"}), 400
    with _locks[session_id]:
        _sessions[session_id].switch_model(model)
    return jsonify({"session_id": session_id, "model": _sessions[session_id].config.model})


@app.route("/session/<session_id>/save", methods=["POST"])
def save_session(session_id: str):
    if session_id not in _sessions:
        return jsonify({"error": "not_found"}), 404
    with _locks[session_id]:
        path = save_history(_sessions[session_id].history)
    return jsonify({"path": str(path), "messages": len(_sessions[session_id].history)})


@app.route("/video/generate", methods=["POST"])
def video_generate():
    data = request.get_json(force=True) or {}
    description = data.get("description")
    if not description:
        return jsonify({"error": "missing description"}), 400
    negative_keywords = data.get("negative_keywords") or []
    _ensure_base_session()
    # reuse first session for google client
    sid = next(iter(_sessions.keys()))
    session = _sessions[sid]
    try:
        client = session.google_client()
        path = generate_veo3_video(client, description=description, negative_keywords=negative_keywords)
    except Exception as e:
        path = f"<error: {e}>"
    status = "ok" if not path.startswith("<error") else "error"
    return jsonify({"path": path, "status": status})


@app.route("/hello-test", methods=["POST"])
def hello_test():
    from .buzzcli import run_hello_test
    _ensure_base_session()
    sid = next(iter(_sessions.keys()))
    code = run_hello_test(_sessions[sid].config)
    return jsonify({"ok": code == 0, "detail": f"exit_code={code}"})


"""Initialization hook (Flask 3 removed before_first_request).
We attempt to use before_serving if present, else fall back to a before_request
that only runs the first time. Also call once eagerly at import so sessions are ready
even in environments that don't trigger serving hooks (e.g. tests)."""
_init_done = False

def _init_once():  # idempotent
    global _init_done
    if _init_done:
        return
    _ensure_base_session()
    _init_done = True

if hasattr(app, "before_serving"):
    @app.before_serving  # type: ignore[attr-defined]
    def _before_serving():  # pragma: no cover
        _init_once()
else:  # fallback
    @app.before_request  # pragma: no cover
    def _before_request():
        _init_once()

# Eager init
_init_once()


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=8000, debug=True)
