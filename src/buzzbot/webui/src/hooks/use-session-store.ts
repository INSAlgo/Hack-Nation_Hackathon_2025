import { createWebserverSession } from "@/lib/api";

export type StoredMessage = { role: "user" | "assistant"; content: string };
export type SessionMeta = { id: string; title: string; updatedAt: number };

const SESSIONS_KEY = "buzzbot_sessions_v1";
const MSG_PREFIX = "buzzbot_msgs_v1:";

function readJSON<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeJSON<T>(key: string, value: T) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {}
}

function readSessions(): SessionMeta[] {
  return readJSON<SessionMeta[]>(SESSIONS_KEY, []);
}

function writeSessions(list: SessionMeta[]) {
  writeJSON(SESSIONS_KEY, list);
}

export function getSessionsSorted(): SessionMeta[] {
  const list = readSessions();
  return [...list].sort((a, b) => b.updatedAt - a.updatedAt);
}

export function upsertSession(meta: SessionMeta) {
  const list = readSessions();
  const idx = list.findIndex((s) => s.id === meta.id);
  if (idx >= 0) list[idx] = meta; else list.push(meta);
  writeSessions(list);
}

export function getMessagesForSession(id: string): StoredMessage[] {
  return readJSON<StoredMessage[]>(MSG_PREFIX + id, []);
}

export function saveMessagesForSession(id: string, msgs: StoredMessage[]) {
  writeJSON(MSG_PREFIX + id, msgs);
  // touch updatedAt
  const list = readSessions();
  const idx = list.findIndex((s) => s.id === id);
  if (idx >= 0) {
    list[idx] = { ...list[idx], updatedAt: Date.now() };
    writeSessions(list);
  }
}

export async function createNewSession(title = "New session"): Promise<SessionMeta> {
  const data = await createWebserverSession();
  const meta: SessionMeta = { id: data.session_id, title, updatedAt: Date.now() };
  const list = readSessions();
  list.push(meta);
  writeSessions(list);
  // initialize empty messages store for this session
  writeJSON(MSG_PREFIX + meta.id, []);
  return meta;
}
