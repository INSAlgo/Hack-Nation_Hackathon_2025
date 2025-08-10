#!/usr/bin/env python3
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .config import AppConfig
from .io_utils import save_history, load_history, print_message, colorize
from .chat import ChatSession


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="buzzbot_cli", description="Minimal terminal chat to OpenAI-compatible models.")
    p.add_argument("--session", type=str, help="Path to existing session JSONL to continue", default=None)
    p.add_argument("--multiline", action="store_true", help="Enable multiline prompt input mode")
    p.add_argument("--system", type=str, help="Override/add a system prompt for this run", default=None)
    p.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    p.add_argument("--test-openai", action="store_true", help="Run a quick 'Hello world' API test and exit")
    # Webserver mode options
    p.add_argument("--webserver", action="store_true", help="Start web server (Flask) instead of interactive CLI (default)")
    p.add_argument("--webserver-host", type=str, default="0.0.0.0", help="Host to bind web server (default: 0.0.0.0)")
    p.add_argument("--webserver-port", type=int, default=8000, help="Port for web server (default: 8000)")
    p.add_argument("--webserver-reload", action="store_true", help="Enable autoreload for web server (dev only)")
    p.add_argument("--cli", action="store_true", help="Force CLI mode (override default webserver)")
    return p.parse_args(argv)


def read_multiline() -> str:
    print("(finish with empty line)")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)


def repl(session: ChatSession):
    print(colorize("Type /exit to quit, /save to persist, /new to reset, /model <name> to switch model.", "\033[33m", session.config.color))
    while True:
        try:
            prompt = input(colorize("you> ", "\033[32m", session.config.color))
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not prompt.strip():
            continue
        if prompt.startswith('/'):
            if prompt.strip() == '/exit':
                break
            if prompt.strip() == '/save':
                path = save_history(session.history)
                print(f"Saved to {path}")
                continue
            if prompt.strip() == '/new':
                model = session.config.model
                session.history.clear()
                if session.config.system_prompt:
                    session.history.append({"role": "system", "content": session.config.system_prompt})
                print("Started new session (model remains: %s)" % model)
                continue
            if prompt.startswith('/model'):
                parts = prompt.split(maxsplit=1)
                if len(parts) == 2 and parts[1].strip():
                    new_model = parts[1].strip()
                    session.switch_model(new_model)
                    print(f"Switched model to {new_model}")
                else:
                    print("Usage: /model <model_name>")
                continue
            print("Unknown command.")
            continue
        session.complete(prompt)


def repl_multiline(session: ChatSession):
    print(colorize("Multiline mode. End input with empty line. /exit etc. still supported (single line).", "\033[33m", session.config.color))
    while True:
        try:
            first = input(colorize("you| ", "\033[32m", session.config.color))
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not first.strip():
            continue
        if first.startswith('/'):
            # allow commands without entering multiline capture
            if first.strip() == '/exit':
                break
            if first.strip() == '/save':
                path = save_history(session.history)
                print(f"Saved to {path}")
                continue
            if first.strip() == '/new':
                model = session.config.model
                session.history.clear()
                if session.config.system_prompt:
                    session.history.append({"role": "system", "content": session.config.system_prompt})
                print("Started new session (model remains: %s)" % model)
                continue
            if first.startswith('/model'):
                parts = first.split(maxsplit=1)
                if len(parts) == 2 and parts[1].strip():
                    new_model = parts[1].strip()
                    session.switch_model(new_model)
                    print(f"Switched model to {new_model}")
                else:
                    print("Usage: /model <model_name>")
                continue
            print("Unknown command.")
            continue
        lines = [first]
        print("(continue input; empty line to send)")
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == "":
                break
            lines.append(line)
        content = "\n".join(lines)
        session.complete(content)


# ------------------------- Test helper ---------------------------------------

def run_hello_test(config: AppConfig) -> int:
    """Perform a minimal API round-trip and print result.
    Returns exit code.
    """
    print("Running API test (model=%s)..." % config.model)
    try:
        session = ChatSession(config=config)
        client = session.openai_client()
        resp = client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": "Say 'Hello world' exactly."}],
            stream=False,
        )
        content = resp.choices[0].message.content.strip()
        print("Assistant:", content)
        if "hello world" in content.lower():
            print("[success] API test passed.")
            return 0
        print("[warn] API responded but content unexpected.")
        return 2
    except Exception as e:
        print(f"[error] API test failed: {e}")
        return 1

# ----------------------------------------------------------------------------
