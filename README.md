<div align="center">

# Global AI Hackathon 2025 – BuzzBot

> This repository contains the [INSAlgo](https://insalgo.fr/) team project for entry 12: Building a viral video-making app of the [Global AI Hackathon 2025 by Hack-Nation](https://hack-nation.ai/) that took place on *August 9-10, 2025*. Team was composed of [Onyr (Florian Rascoussier)](https://github.com/0nyr), [WiredMind2 (William Michaud)](https://github.com/WiredMind2), & [Pichu (Ngoc Ha Dao)](https://github.com/pichu2405).
>
> [Onyr's postmortem post on Linkedin](https://www.linkedin.com/posts/florian-rascoussier-onyr_hacknation2025-mitaihackathon-globalaihackathon-activity-7360421902630199296-4JPm?utm_source=share&utm_medium=member_desktop&rcm=ACoAACcIsOkB0IhxGhcova4MtLZJQQzTt0Z5e0Q)
> [Hackathon organizers Linkedin page](https://www.linkedin.com/company/hack-nation/)

Unified conversational + video generation assistant (CLI & Web) built during the Global AI Hackathon (deadline Aug 10, 09:00 ET). Team: **INSAlgo**.

</div>

## 🚀 Short Description (150–300 words)
BuzzBot unifies ideation, iteration, and early media generation for short‑form content creators who currently juggle separate LLM chat tabs, video tools, and manual file handling. Within the hackathon window we built a minimal, *extensible* assistant that: (1) provides a fast terminal and web chat interface to OpenAI‑compatible models; (2) supports structured tool/function calling (extending the model with deterministic Python functions); (3) integrates Google Veo 3 preview to generate short videos directly from within a conversation; (4) persists sessions in both SQLite and portable JSONL, auto‑generating semantic titles after sufficient context; and (5) exposes a thin API layer that can later orchestrate social distribution. The core `ChatSession` loop implements a robust tool‑calling phase (non‑streaming until tools are resolved, then graceful fallback) while keeping the code surface small. Extensibility requires only adding a JSON schema entry + dispatcher mapping. A React/Vite/Tailwind frontend consumes the same REST endpoints the CLI uses, demonstrating interface parity. Although we intentionally deferred advanced auth, async background workers, and full publishing, the delivered MVP proves the architecture: a single conversational nucleus augmented by composable tools bridging creative intent to media artifacts.

## 📅 Key Event Milestones
- Team/challenge lock‑in: Aug 9 (13:15 ET)  
- Final submission deadline: Aug 10 (09:00 ET)  
- Credits request window (Lovable / ElevenLabs): until Aug 10 (13:15 ET)  

## 🧩 Challenges We Target
Fragmented workflow & context loss between brainstorming (LLM), media generation, and draft social distribution.

## 🛠 Tech Stack
| Layer | Technologies |
|-------|--------------|
| Core Chat / Tools | Python, OpenAI SDK (`chat.completions` function calling), custom tool dispatcher |
| Video Generation | Google Veo 3 preview (`google-genai`) |
| Backend API | Flask, SQLAlchemy (SQLite), threading locks |
| Persistence | SQLite (`buzzbot.db`), JSONL session export, filesystem video artifacts |
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, Radix UI components |
| Dev / Ops | `uv` (venv + deps), requirements freeze, smoke tests |

## 🧱 Architecture Overview
```
		  ┌────────────────┐
CLI (buzzcli) ─▶│ ChatSession    │◀─ Web UI (React)
		  │  (history,    │
		  │  tool loop)   │
		  └─────┬─────────┘
			 │
	   Function Call Dispatcher
	 (dice, Veo3 video, future tools)
			 │
	   ┌───────────┴───────────┐
	   │                       │
   OpenAI-compatible API     Google Veo 3
	   │                       │
      LLM Responses        Long Op Polling
			 │
	     Persistence Layer (SQLite + JSONL)
```

## 📂 Repository Layout (Key Parts)
- `src/buzzbot/chat.py` – Core chat + tool invocation loop.
- `src/buzzbot/veo3.py` – Veo 3 video generation (polling + artifact save).
- `src/buzzbot/webserver.py` – Flask REST API & session endpoints.
- `src/buzzbot/buzzcli.py` – Interactive terminal client & commands.
- `src/buzzbot/models.py` – SQLAlchemy models (User, ChatSessionDB, MessageDB).
- `src/buzzbot/webui/` – React/Vite frontend.
- `data/sessions/` – JSONL archived sessions.
- `instance/buzzbot.db` – SQLite database (created at runtime).

## ⚙️ Environment Variables
Create `env/.env` or export before running:
```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1   # optional override
OPENAI_MODEL=gpt-4o-mini                    # optional
OPENAI_SYSTEM_PROMPT=You are a helpful assistant.  # optional
GOOGLE_API_KEY=...                          # required for Veo3 tool
NO_COLOR=0                                  # set to 1 to disable ANSI
DEBUG=0                                     # set 1 for verbose tool debug
```

## 🔧 Backend Setup & Run (Linux/macOS)
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp env/.env.example env/.env  # if example exists, then edit values
python -m src.buzzbot.webserver  # starts Flask API (default 8000)
```

### Windows (PowerShell)
```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m src.buzzbot.webserver
```

## 💬 CLI Usage
```bash
python src/main.py --help
python src/main.py                # single prompt loop
python src/main.py --multiline    # multiline entry
python src/main.py --session sessions/<file>.jsonl
```
In-chat commands: `/exit`, `/save`, `/new`, `/model <name>`.

## 🌐 Web UI
Install Node deps inside `src/buzzbot/webui/`:
```bash
cd src/buzzbot/webui
npm install
npm run dev     # or: npm run build && npm run preview
```
Ensure backend (Flask) is running; the frontend will call `/chat`, `/sessions`, etc.

## 🧪 Testing (Smoke)
`tests_smoke.py` validates basic chat loop and save/load roundtrip:
```bash
python tests_smoke.py
```

## ➕ Extending Tools
1. Add JSON schema entry in `ChatSession._tool_specs()`.
2. Map name → Python callable in `_tool_dispatch`.
3. Implement function (pure, deterministic preferred) returning a string.
4. (Optional) Add persistence or artifact storage.

## 🗃 Submission Assets Mapping
| Requirement | Location / Plan |
|-------------|-----------------|
| Short Description | README (this section) |
| Demo Video | (To add link) |
| Tech Video | (To add link) |
| 1‑Page Report PDF | `Report.md` (export to PDF) |
| GitHub Repo | This repository |
| Zipped Code | Generate via `git archive` or zip root dir |
| Dataset | N/A (no external dataset) |

## 🧱 Known Limitations / Future Work
- No production auth / rate limiting (User model placeholder).
- Veo3 long operations are synchronous polling (future: async task queue + WebSocket/SSE progress).
- Social posting endpoint is a stub; integrate platform APIs + scheduling.
- Add richer evaluation tests and parameter controls (temperature, top‑p).

## 👥 Team (Placeholders – fill before submission)
- Backend & Tooling: _Name_
- Frontend & UX: _Name_
- Infra / DevOps: _Name_
- Integration & QA: _Name_

## 🤝 Contributing
External contributions outside hackathon scope: fork + PR (lightweight code review encouraged).

## 📄 License
Hackathon prototype – license to be finalized (assume internal evaluation use only until updated).

---

# BuzzBot CLI (Original Quick Reference)

Minimal terminal chat client for OpenAI-compatible models using `openai-agents` (retained for convenience).

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
