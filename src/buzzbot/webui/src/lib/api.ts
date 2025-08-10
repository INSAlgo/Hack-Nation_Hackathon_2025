// Webserver utility for BuzzBot Flask backend
export async function chatWithWebserver({ prompt, sessionId }: { prompt: string, sessionId?: string }) {
  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, session_id: sessionId }),
  });
  if (!res.ok) throw new Error("Webserver error");
  return res.json();
}

export async function createWebserverSession() {
  const res = await fetch("/session/new", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}), // Always send a valid JSON body
  });
  if (!res.ok) throw new Error("Webserver error");
  return res.json();
}

export async function getSessionTitle(sessionId: string) {
  const res = await fetch(`/session/${sessionId}/title`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Webserver error");
  return res.json();
}

// Fetch all sessions from the backend
export async function getSessions() {
  const res = await fetch("/sessions", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Webserver error");
  return res.json(); // Should return an array of {id, title, updatedAt}
}

export async function deleteWebserverSession(sessionId: string) {
  const res = await fetch(`/session/${sessionId}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Webserver error");
  return res.json();
}
