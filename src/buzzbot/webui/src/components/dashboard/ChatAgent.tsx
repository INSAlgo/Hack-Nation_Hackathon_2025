import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState, useRef, useEffect } from "react";

import { chatWithWebserver, getSessionTitle } from "@/lib/api";
import { getMessagesForSession, saveMessagesForSession } from "@/hooks/use-session-store";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Send } from "lucide-react";



interface Message {
  role: "user" | "assistant";
  content: string;
  video_status?: "generating";
  video_url?: string;
}


const initialAssistantMsg = "Hey! I’m your TikTok Igniter AI. Tell me your niche and vibe (funny, educational, edgy) and I’ll craft a scroll-stopping hook, 15–30s script, B-roll ideas, and caption/hashtags.";


type ChatAgentProps = {
  sessionId?: string;
  onVideoStatus?: (status: "idle"|"generating") => void;
  onVideoUrl?: (url?: string) => void;
  onSessionTitle?: (sessionId: string, title: string) => void;
};

export default function ChatAgent({ sessionId, onVideoStatus, onVideoUrl, onSessionTitle }: ChatAgentProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionTitle, setSessionTitle] = useState<string | undefined>(undefined);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);


  useEffect(() => {
    if (!sessionId) return;
    const existing = getMessagesForSession(sessionId);
    if (existing && existing.length) {
      setMessages(existing);
      // Try to get a session title if there are at least 2 user messages
      const userMsgs = existing.filter((m) => m.role === "user");
      if (userMsgs.length >= 2) {
        getSessionTitle(sessionId)
          .then((res) => {
            if (res.title) {
              setSessionTitle(res.title);
              onSessionTitle?.(sessionId, res.title);
            }
          })
          .catch(() => {});
      }
    } else {
      setMessages([{ role: "assistant", content: initialAssistantMsg }]);
    }
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) return;
    saveMessagesForSession(sessionId, messages);
    // Try to get a session title if there are at least 2 user messages and no title yet
    const userMsgs = messages.filter((m) => m.role === "user");
    if (userMsgs.length >= 2 && !sessionTitle) {
      getSessionTitle(sessionId)
        .then((res) => {
          if (res.title) {
            setSessionTitle(res.title);
            onSessionTitle?.(sessionId, res.title);
          }
        })
        .catch(() => {});
    }
  }, [messages, sessionId]);

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;
    const userMsg = { role: "user" as const, content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await chatWithWebserver({ prompt: userMsg.content, sessionId });
      // Detect video generation status in response
      if (res.video_status === "generating") {
        onVideoStatus?.("generating");
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Generating video preview...", video_status: "generating" },
        ]);
      } else if (res.video_url) {
        onVideoStatus?.("idle");
        onVideoUrl?.(res.video_url);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Video is ready!", video_url: res.video_url },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: res.reply || "(No reply)" },
        ]);
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, there was an error contacting the AI webserver." },
      ]);
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="sr-only">
        <h2>AI Agent</h2>
        <p>Craft viral TikTok hooks, scripts, and captions.</p>
      </div>
      {sessionTitle && (
        <div className="mb-2 text-center text-xs text-muted-foreground font-semibold">Session: {sessionTitle}</div>
      )}
      <div className="flex-1 min-h-0">
        <ScrollArea className="h-full pr-3">
          <div className="space-y-3">
            {messages.map((m, i) => (
              <div key={i} className="flex">
                <div
                  className={
                    m.role === "user"
                      ? "ml-auto max-w-[85%] rounded-md bg-secondary text-secondary-foreground px-3 py-2"
                      : "mr-auto max-w-[85%] rounded-md bg-muted px-3 py-2"
                  }
                >
                  {m.role === "assistant" ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {m.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{m.content}</p>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex">
                <div className="mr-auto max-w-[85%] rounded-md bg-muted px-3 py-2">
                  <p className="text-sm animate-pulse">Thinking…</p>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      <div className="space-y-2 pt-3">
        <div className="relative">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your idea (niche, hook angle, vibe)…"
            className="pr-12"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={sendMessage}
            disabled={loading}
            aria-label="Send message"
            className="absolute bottom-2 right-2"
          >
            <Send />
            <span className="sr-only">Send</span>
          </Button>
        </div>
        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">Press Enter to send, Shift+Enter for new line</p>
        </div>
      </div>
    </div>
  );
}
