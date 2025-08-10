# Global AI Hackathon 2025

We are participating in the name of [INSAlgo](https://insalgo.fr/), as the INSAlgo hackathon team.

### General Infos
 - Starts: Saturday 19th August, 10:00 EST
 - Submission ends: Sunday 20th, August, 9:00 EST (15:00 Paris)
 - Winners announcement: Sunday 20th, August, 14:00 EST (20:00 Paris)

---

# BuzzBot CLI

Minimal terminal chat client for OpenAI-compatible models using `openai-agents`.

## Features
- Streamed token output (falls back gracefully if streaming unsupported)
- Commands: `/exit`, `/save`, `/new`, `/model <name>`
- Multiline input mode (`--multiline`)
- Session persistence to JSONL (one message per line)
- Reload prior session with `--session path/to/file.jsonl`
- System prompt injection with `--system "You are..."`
- ANSI color (disable with `--no-color` or env NO_COLOR=1)

## Install, Handle dependencies, and Run
```bash
uv venv .venv
source .venv/bin/activate
uv pip install --upgrade pip
uv pip install -r requirements.txt
uv pip freeze > requirements.txt
cp .env.example .env  # then edit with your keys (SECRET_KEY, API keys, etc.)
python src/main.py --help
```

## Usage Examples
```bash
OPENAI_API_KEY=sk-... python src/main.py
OPENAI_BASE_URL=http://localhost:8080/v1 OPENAI_MODEL=gpt-4o-mini python src/main.py --multiline
python src/main.py --session sessions/2025-08-09T12-00-00.jsonl
```

## Commands In Chat
- `/exit` quit
- `/save` write `sessions/<timestamp>.jsonl`
- `/new` clear in-memory history (retains current model & system prompt)
- `/model <name>` switch model mid-session

## Session Files
Stored under `sessions/` as UTC timestamped JSONL. Each line is a message object:
```json
{"role": "user", "content": "Hello"}
{"role": "assistant", "content": "Hi there!"}
```

Load an existing session:
```bash
python src/main.py --session sessions/2025-08-09T12-00-00.jsonl
```

## Streaming
Tokens are printed as they arrive. If streaming errors occur, a warning prints and the client falls back to a single non-streaming response.

## Testing (Smoke)
A lightweight `tests_smoke.py` is included to validate:
- Chat loop can append a mock assistant reply
- JSONL save/load roundtrip

Run:
```bash
python tests_smoke.py
```

## Extensibility Notes
- Add new provider support in `chat.py` (abstract client creation / response loop).
- Insert tool/function calling logic inside `ChatSession.complete` after accumulating full assistant message.
- Add richer CLI flags in `buzzcli.py` (e.g., `--temperature`, `--top-p`).
- Implement a `/veo` command as a placeholder for future tool integration.
- For different model gateways, just set `OPENAI_BASE_URL` (must be OpenAI-compatible).

## Requirements
Pinned in `requirements.txt`. Adjust version of `openai-agents` as needed if streaming API surface changes.

## Troubleshooting
- Missing key: ensure `OPENAI_API_KEY` is set (env or `.env`).
- Connection errors: verify `OPENAI_BASE_URL` and network reachability.
- Model errors: try switching with `/model gpt-4o-mini` or another available model.
