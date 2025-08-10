# BuzzBot – 1‑Page Report

## 1) Challenge You Have Tackled
Creators who ideate, refine, and distribute short‑form video content juggle multiple disconnected tools: an LLM chat for brainstorming, a separate video generation UI, manual file handling, and eventual posting flows. Context (prompt history, model settings, iteration notes) is frequently lost between steps, slowing experimentation. Our hackathon challenge: prototype a unified, minimal, *extensible* assistant that (a) offers fast conversational iteration, (b) can call structured "tools" (functions) for media generation, (c) persists sessions with semantic titling, and (d) lays groundwork for automated social distribution—while keeping the core small, transparent, and easy to extend in future sprints.

## 2) Tools / ML Models You Have Used
- OpenAI‑compatible Chat Completion models (default: `gpt-4o-mini`) for conversation, tool/function calling, and automatic session title generation.
- Google Veo 3 (preview) via `google-genai` for text‑to‑video generation (polled long‑running operation).
- Function calling loop (custom) to execute registered Python tools: example D6 dice + Veo3 video generator.
- Flask + SQLAlchemy (SQLite) backend for REST API, session & message persistence, and video/job endpoints.
- React + Vite + Tailwind CSS frontend (chat UI scaffold, session listing, responsive hooks).
- Supporting libs/utilities: OpenAI SDK, `google-genai`, threading locks for per‑session concurrency, custom `.env` loader (no external dotenv dependency).

## 3) What Has Worked Well With These Tools?
- Rapid iteration: OpenAI model + structured tool schema let us add new capabilities by appending JSON spec + dispatcher entry (low friction extensibility).
- Reliable fallback: Non‑streaming pass during tool resolution avoided partial tool call confusion, then standard streaming/printing for final answer—improving robustness.
- Automatic semantic titling after two user prompts boosted session organization with minimal extra code (reuse of the same model path).
- Veo3 integration encapsulated in a single `generate_veo3_video` function producing timestamped, hash‑scoped filenames—safe, reproducible artifact storage.
- Thin persistence layer (SQLite) let us reconstruct in‑memory sessions lazily, making restarts and horizontal scaling more straightforward.
- Shared `ChatSession` core used by both CLI and Web reduced duplicate logic, keeping bug surface small.

## 4) What Was Challenging?
- Iterative tool calling edge cases (multiple function calls in one response) required careful ordering: append assistant tool call message *before* tool outputs to satisfy API expectations.
- Long‑running Veo3 operations: designing a bounded polling strategy (timeout + clear error strings) to avoid indefinite hanging during generation.
- Concurrency & consistency: ensuring DB writes (messages, titles) occur atomically relative to in‑memory history—solved with per‑session locks and idempotent reconstruction.
- Title generation recursion risk: avoiding loops when the model call to produce a title itself adds messages—handled by triggering only after plain user messages and checking existing title.
- Scope discipline: resisting feature creep (auth flows, full social posting, streaming WebSockets) to keep a stable MVP within hackathon time.

## 5) How Have You Spent Your Time?
| Phase | Approx. % | Activities |
|-------|-----------|-----------|
| Architecture & Scoping | 10% | MVP definition, extensibility decisions, tool pattern |
| Core Chat & CLI | 20% | `ChatSession`, function call loop, commands, JSONL persistence |
| Backend API & DB | 20% | Flask endpoints, SQLAlchemy models, session restore, locks |
| Veo3 Integration | 10% | Video tool function, polling, file naming/storage |
| Frontend Scaffold | 15% | React/Vite setup, session list, chat wiring, Tailwind styling |
| Enhancements & Titles | 10% | Auto title generation logic, model switching API, cleanup |
| Testing & Hardening | 10% | Smoke tests, fallback paths, error messaging, docs/report |
| Buffer / Debug | 5% | Fix edge cases (timeouts, missing keys), minor refactors |

### Compressed Hour-by-Hour (Illustrative)
0–2h: Brainstorm, scope cut, architecture sketch  
2–6h: Core ChatSession + CLI loop + persistence  
6–10h: Tool schema & dispatcher, dice tool, refactors  
10–14h: Flask API, DB models, session reconstruction  
14–17h: Veo3 integration & polling reliability  
17–20h: Web UI scaffold + session list + chat wiring  
20–22h: Auto title generation, model switch endpoint  
22–24h: Polish, smoke tests, README/report, submission assets  

Total fits within a standard hackathon window (~24–30 effective hours) and leaves clear next‑step seams (async tasks, richer auth, multi‑platform posting, streaming UI).

---
**Dataset:** N/A (only generated conversational logs & video artifacts).  
**Optional Reflection:** If we had 24 more hours we would externalize long‑running tool jobs to an async queue and stream intermediate status to the UI (SSE/WebSocket).  
**Reminder:** Export this file as PDF (e.g. `BuzzBot_OnePager.pdf`) and include links to Demo & Tech videos in the submission form.