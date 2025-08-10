
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState, useRef, useEffect } from "react";

import { chatWithWebserver, createWebserverSession } from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Send } from "lucide-react";


interface Message {
  role: "user" | "assistant";
  content: string;
}


const initialAssistantMsg = "Hey! I’m your TikTok Igniter AI. Tell me your niche and vibe (funny, educational, edgy) and I’ll craft a scroll-stopping hook, 15–30s script, B-roll ideas, and caption/hashtags.";


export default function ChatAgent() {
  const [messages, setMessages] = useState<Message[]>([{
    role: "assistant",
    content: initialAssistantMsg,
  }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);


  useEffect(() => {
    // Create a session on mount
    createWebserverSession().then((data) => {
      setSessionId(data.session_id);
    });
  }, []);

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;
    const userMsg = { role: "user" as const, content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await chatWithWebserver({ prompt: userMsg.content, sessionId });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.reply || "(No reply)" },
      ]);
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
