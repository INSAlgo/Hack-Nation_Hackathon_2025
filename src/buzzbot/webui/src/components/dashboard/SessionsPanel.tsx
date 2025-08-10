import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, MessageSquare, Trash2 } from "lucide-react";
import type { SessionMeta } from "@/hooks/use-session-store";
import { AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel, AlertDialogAction } from "@/components/ui/alert-dialog";

interface SessionsPanelProps {
  sessions: SessionMeta[];
  selectedId?: string;
  onSelect: (id: string) => void;
  onCreate: () => void | Promise<void>;
  onDelete: (id: string) => void | Promise<void>;
}

export default function SessionsPanel({ sessions, selectedId, onSelect, onCreate, onDelete }: SessionsPanelProps) {
  return (
    <aside className="h-full flex flex-col rounded-md border bg-card" aria-label="Sessions panel">
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4" />
          <h2 className="text-sm font-medium">Sessions</h2>
        </div>
        <Button size="sm" onClick={onCreate} aria-label="Start a new session">
          <Plus className="h-4 w-4 mr-2" /> New
        </Button>
      </div>

      <ScrollArea className="flex-1">
        {sessions.length === 0 ? (
          <div className="p-4 text-sm text-muted-foreground">No sessions yet. Create one to get started.</div>
        ) : (
          <ul className="p-2 space-y-1">
            {sessions.map((s) => (
              <li key={s.id}>
                <div
                  className={`flex items-center rounded-md transition-colors ${
                    s.id === selectedId ? "bg-muted" : "hover:bg-muted/60"
                  }`}
                >
                  <button
                    onClick={() => onSelect(s.id)}
                    className="flex-1 text-left px-3 py-2"
                    aria-current={s.id === selectedId ? "page" : undefined}
                  >
                    <div className="text-sm font-medium truncate">{s.title || `Session ${s.id.slice(-6)}`}</div>
                    <div className="text-xs text-muted-foreground">{new Date(s.updatedAt).toLocaleString()}</div>
                  </button>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="ghost" size="icon" aria-label={`Delete ${s.title || "session"}`}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Delete session?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This will permanently remove this session and its messages. This action cannot be undone.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={() => onDelete(s.id)}
                        >
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </li>
            ))}
          </ul>
        )}
      </ScrollArea>
    </aside>
  );
}
