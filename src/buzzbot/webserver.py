from __future__ import annotations
"""Flask implementation of the BuzzBot Web Server (API layer)."""

# =====================
# Imports
# =====================
import logging
import threading
import traceback
import uuid
from pathlib import Path as _Path
from typing import Dict, List, Optional, Any

from flask import Flask, request, jsonify, send_from_directory, session as flask_session
from werkzeug.security import generate_password_hash, check_password_hash

from .models import db, User, ChatSessionDB, MessageDB
from .config import AppConfig
from .chat import ChatSession
from .io_utils import save_history
from .veo3 import generate_veo3_video

# =====================
# Path and App Initialization
# =====================
BASE_DIR = _Path(__file__).resolve().parent
WEBUI_DIR = BASE_DIR / 'webui'
WEBUI_DIST_DIR = WEBUI_DIR / 'dist'
WEBUI_INDEX = WEBUI_DIST_DIR / 'index.html'

app = Flask(
    __name__,
    static_folder=str(WEBUI_DIST_DIR),
    static_url_path=''
)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buzzbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'replace-this-with-a-secret-key'
db.init_app(app)
with app.app_context():
    db.create_all()

# =====================
# Global Config & State
# =====================
_config = AppConfig.load()
_sessions: Dict[str, ChatSession] = {}
_locks: Dict[str, threading.Lock] = {}
_global_lock = threading.Lock()

# =====================
# Utility Functions
# =====================
def _create_session(model: Optional[str] = None, system_prompt: Optional[str] = None, user_id: Optional[int] = None) -> str:
    from flask import has_request_context
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
    # Save to DB
    with app.app_context():
        if user_id is not None:
            db_user_id = user_id
        elif has_request_context():
            db_user_id = flask_session.get('user_id') or 0
        else:
            db_user_id = 0
        db.session.add(ChatSessionDB(user_id=db_user_id, session_id=sid))
        db.session.commit()
    return sid

def _ensure_base_session():
    if not _sessions:
        _create_session()

def _session_payload(session_id: str):
    s = _sessions[session_id]
    # Try to get a title from the DB if it exists
    title = None
    csdb = ChatSessionDB.query.filter_by(session_id=session_id).first()
    if csdb and hasattr(csdb, 'title') and csdb.title:
        title = csdb.title
    else:
        # Try to generate a title if enough messages
        msgs = MessageDB.query.filter_by(session_id=session_id, role="user").order_by(MessageDB.timestamp).all()
        if len(msgs) >= 2:
            def first_words(text, n=6):
                return " ".join(text.split()[:n])
            first = msgs[0].content.strip()
            second = msgs[1].content.strip()
            title = f"{first_words(first)} / {first_words(second)}"
        else:
            title = None
    return {
        "session_id": session_id,
        "model": s.config.model,
        "system_prompt": s.config.system_prompt,
        "messages": len(s.history),
        "title": title,
    }

# =====================
# Session List Endpoint
# =====================
@app.route("/sessions", methods=["GET"])
def list_sessions():
    # List all sessions for the current user (or all if not using user auth)
    user_id = flask_session.get('user_id') if 'user_id' in flask_session else None
    if user_id:
        sessions = ChatSessionDB.query.filter_by(user_id=user_id).all()
    else:
        sessions = ChatSessionDB.query.all()
    result = []
    for s in sessions:
        # Determine title
        title = getattr(s, 'title', None)
        if not title:
            msgs = MessageDB.query.filter_by(session_id=s.session_id, role="user").order_by(MessageDB.timestamp).all()
            if len(msgs) >= 2:
                def first_words(text, n=6):
                    return " ".join(text.split()[:n])
                first = msgs[0].content.strip()
                second = msgs[1].content.strip()
                title = f"{first_words(first)} / {first_words(second)}"
            elif msgs:
                title = msgs[0].content.strip()[:40]
            else:
                title = "Session"
        created_at = getattr(s, 'created_at', None)
        updated_at = getattr(s, 'updated_at', None)
        def ts(dt):
            if not dt:
                return None
            try:
                return int(dt.timestamp() * 1000)
            except Exception:
                return None
        result.append({
            "id": s.session_id,
            "title": title,
            "createdAt": ts(created_at),
            "updatedAt": ts(updated_at) or ts(created_at),
        })
    # Sort by updatedAt desc
    result.sort(key=lambda x: x.get("updatedAt") or 0, reverse=True)
    return jsonify(result)

@app.route("/session/<session_id>", methods=["DELETE"])
def delete_session(session_id: str):
    cs = ChatSessionDB.query.filter_by(session_id=session_id).first()
    if not cs:
        return jsonify({"error": "Session not found"}), 404
    # Delete messages
    MessageDB.query.filter_by(session_id=session_id).delete()
    # Delete session row
    db.session.delete(cs)
    db.session.commit()
    # Remove from in-memory store if present
    _sessions.pop(session_id, None)
    _locks.pop(session_id, None)
    return jsonify({"ok": True})

# =====================
# Error Handling
# =====================
@app.errorhandler(Exception)
def handle_exception(e):
    # Log full traceback to console
    logging.error("Exception on request: %s", request.path)
    traceback.print_exc()
    # Return JSON error
    return jsonify({"error": str(e), "type": type(e).__name__}), getattr(e, "code", 500)

# =====================
# CORS
# =====================
@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "*"
    return resp

# =====================
# Health & Frontend
# =====================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/")
@app.route("/<path:path>")
def serve_frontend(path=None):
    if path and (WEBUI_DIST_DIR / path).exists():
        return send_from_directory(str(WEBUI_DIST_DIR), path)
    return send_from_directory(str(WEBUI_DIST_DIR), "index.html")

# =====================
# Session & Chat Endpoints
# =====================
@app.route("/session/new", methods=["POST"])
def session_new():
    data = request.get_json(force=True) or {}
    sid = _create_session(model=data.get("model"), system_prompt=data.get("system_prompt"))
    return jsonify(_session_payload(sid))

@app.route("/session/<session_id>", methods=["GET"])
def get_session(session_id: str):
    if session_id not in _sessions:
        # Try to restore from DB
        csdb = ChatSessionDB.query.filter_by(session_id=session_id).first()
        if not csdb:
            return jsonify({"error": "not_found"}), 404
        # Load messages
        msgs = MessageDB.query.filter_by(session_id=session_id).order_by(MessageDB.timestamp).all()
        history = [{"role": m.role, "content": m.content} for m in msgs]
        # Recreate ChatSession
        session = ChatSession(config=_config, history=history)
        _sessions[session_id] = session
        _locks[session_id] = threading.Lock()
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
        # Save user message to DB
        with app.app_context():
            db.session.add(MessageDB(session_id=sid, role="user", content=prompt))
            db.session.commit()

            # --- Auto-generate session title after 2 user messages ---
            user_msgs = MessageDB.query.filter_by(session_id=sid, role="user").order_by(MessageDB.timestamp).all()
            csdb = ChatSessionDB.query.filter_by(session_id=sid).first()
            if len(user_msgs) == 2 and csdb and (not hasattr(csdb, 'title') or not csdb.title):
                # Compose a prompt for the LLM
                history = [
                    {"role": m.role, "content": m.content}
                    for m in MessageDB.query.filter_by(session_id=sid).order_by(MessageDB.timestamp).all()
                ]
                llm_prompt = (
                    "Given the following chat session history, generate a short, descriptive title (max 12 words) that summarizes the main topic or purpose.\n"
                    "Session history:\n"
                )
                for m in history:
                    llm_prompt += f"{m['role']}: {m['content']}\n"
                llm_prompt += "\nTitle: "
                title = None
                if session and hasattr(session, 'complete'):
                    try:
                        ai_response = session.complete(llm_prompt)
                        if isinstance(ai_response, dict):
                            title = ai_response.get("content", "").strip().split("\n")[0]
                        elif isinstance(ai_response, str):
                            title = ai_response.strip().split("\n")[0]
                        title = " ".join(title.split()[:12]) if title else None
                    except Exception:
                        title = None
                # Fallback to heuristic
                if not title:
                    def first_words(text, n=6):
                        return " ".join(text.split()[:n])
                    first = user_msgs[0].content.strip()
                    second = user_msgs[1].content.strip()
                    title = f"{first_words(first)} / {first_words(second)}"
                try:
                    csdb.title = title
                    db.session.commit()
                except Exception:
                    db.session.rollback()

        reply_msg = session.complete(prompt)
        # Save assistant message to DB
        if reply_msg.get("content"):
            with app.app_context():
                db.session.add(MessageDB(session_id=sid, role="assistant", content=reply_msg["content"]))
                db.session.commit()
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

# =====================
# Video & Social Endpoints
# =====================
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

@app.route("/post/start", methods=["POST"])
def post_start():
    """
    Start posting a video to selected social media platforms.
    Expects JSON: {"video_url": str, "description": str, "platforms": [str], ...}
    """
    data = request.get_json(force=True) or {}
    video_url = data.get("video_url")
    description = data.get("description")
    platforms = data.get("platforms")
    # Optionally: hashtags, schedule, etc.
    if not video_url or not description or not platforms:
        return jsonify({"error": "Missing required fields (video_url, description, platforms)"}), 400
    # Here you would trigger the actual posting logic (async task, API call, etc.)
    # For now, just log and return success
    logging.info(f"Posting video {video_url} to platforms: {platforms} with description: {description}")
    # TODO: Integrate with actual social media APIs
    return jsonify({"ok": True, "message": "Posting started", "platforms": platforms})

# =====================
# Miscellaneous Endpoints
# =====================
@app.route("/hello-test", methods=["POST"])
def hello_test():
    from .buzzcli import run_hello_test
    _ensure_base_session()
    sid = next(iter(_sessions.keys()))
    code = run_hello_test(_sessions[sid].config)
    return jsonify({"ok": code == 0, "detail": f"exit_code={code}"})

@app.route("/session/<session_id>/title", methods=["POST"])
def generate_session_title(session_id):
    """
    Generate a session title after the user has sent at least two messages.
    Returns: {"title": str}
    """
    # Find messages for this session
    msgs = MessageDB.query.filter_by(session_id=session_id).order_by(MessageDB.timestamp).all()
    if len(msgs) < 2:
        return jsonify({"error": "Not enough user messages to generate a title."}), 400
    # Compose a prompt for the LLM
    history = [
        {"role": m.role, "content": m.content}
        for m in msgs
    ]
    prompt = (
        "Given the following chat session history, generate a short, descriptive title (max 12 words) that summarizes the main topic or purpose.\n"
        "Session history:\n"
    )
    for m in history:
        prompt += f"{m['role']}: {m['content']}\n"
    prompt += "\nTitle: "

    # Use the session's LLM to generate a title
    session = _sessions.get(session_id)
    title = None
    if session and hasattr(session, 'complete'):
        try:
            ai_response = session.complete(prompt)
            if isinstance(ai_response, dict):
                title = ai_response.get("content", "").strip().split("\n")[0]
            elif isinstance(ai_response, str):
                title = ai_response.strip().split("\n")[0]
            # Truncate to 12 words
            title = " ".join(title.split()[:12]) if title else None
        except Exception:
            title = None

    # Fallback to old heuristic if LLM fails
    if not title:
        user_msgs = [m for m in msgs if m.role == "user"]
        if len(user_msgs) >= 2:
            def first_words(text, n=6):
                return " ".join(text.split()[:n])
            first = user_msgs[0].content.strip()
            second = user_msgs[1].content.strip()
            title = f"{first_words(first)} / {first_words(second)}"
        elif user_msgs:
            title = user_msgs[0].content.strip()[:40]
        else:
            title = "Session"

    # Save the title to the DB if not already saved
    csdb = ChatSessionDB.query.filter_by(session_id=session_id).first()
    if csdb and (not hasattr(csdb, 'title') or not csdb.title):
        try:
            csdb.title = title
            db.session.commit()
        except Exception:
            db.session.rollback()
    return jsonify({"title": title})

# =====================
# Initialization Hooks
# =====================
# =====================
# Initialization Hooks
# =====================
# Initialization hook (Flask 3 removed before_first_request).
# We attempt to use before_serving if present, else fall back to a before_request
# that only runs the first time. Also call once eagerly at import so sessions are ready
# even in environments that don't trigger serving hooks (e.g. tests).
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


