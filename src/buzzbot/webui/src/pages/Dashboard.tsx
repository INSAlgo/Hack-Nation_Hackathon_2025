import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import ChatAgent from "@/components/dashboard/ChatAgent";
import VideoPanel from "@/components/dashboard/VideoPanel";
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from "@/components/ui/resizable";
import SessionsPanel from "@/components/dashboard/SessionsPanel";
import { Button } from "@/components/ui/button";
import { PanelRightOpen, PanelRightClose, Plus } from "lucide-react";
import { getSessionsSorted, createNewSession, type SessionMeta } from "@/hooks/use-session-store";

const Dashboard = () => {
  const title = "BuzzBot – Viral Video Generator";
  const description = "Create viral TikTok hooks, scripts, and captions with AI, then preview instantly.";
  const canonical = typeof window !== "undefined" ? window.location.origin + "/app" : "/app";

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "TikTok Igniter AI",
    applicationCategory: "CreativeWorkApplication",
    description,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    url: canonical,
  };

  const [showSessions, setShowSessions] = useState(true);
  const [sessions, setSessions] = useState<SessionMeta[]>([]);
  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);

  useEffect(() => {
    const list = getSessionsSorted();
    if (list.length === 0) {
      createNewSession().then((meta) => {
        setSessions(getSessionsSorted());
        setSelectedId(meta.id);
      });
    } else {
      setSessions(list);
      setSelectedId(list[0].id);
    }
  }, []);

  const handleSelect = (id: string) => setSelectedId(id);
  const handleNew = async () => {
    const meta = await createNewSession();
    setSessions(getSessionsSorted());
    setSelectedId(meta.id);
    setShowSessions(true);
  };

  return (
    <>
      <Helmet>
        <title>{title}</title>
        <meta name="description" content={description} />
        <link rel="canonical" href={canonical} />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
      </Helmet>

      {/* App title bar */}
      <header className="h-14 w-full border-b bg-background px-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link to="/">
            <button className="text-sm font-medium text-muted-foreground hover:underline focus:outline-none">
              BuzzBot
            </button>
          </Link>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setShowSessions((v) => !v)}>
            {showSessions ? (
              <PanelRightClose className="mr-2 h-4 w-4" />
            ) : (
              <PanelRightOpen className="mr-2 h-4 w-4" />
            )}
            Sessions
          </Button>
          <Button size="sm" onClick={handleNew}>
            <Plus className="mr-2 h-4 w-4" />
            New session
          </Button>
        </div>
      </header>

      {/* Main layout: left video, center chat, right sessions */}
      <div className="flex min-h-[calc(100dvh-3.5rem)] w-full overflow-hidden">
        <aside className="hidden lg:block w-[380px] xl:w-[420px] p-4 overflow-auto" aria-label="Video panel">
          <VideoPanel />
        </aside>
        <main className="flex-1 overflow-hidden p-4" aria-label="AI chat and sessions">
          <h1 className="sr-only">Create Viral TikToks with AI</h1>
          <div className="h-full">
            {showSessions ? (
              <ResizablePanelGroup direction="horizontal">
                <ResizablePanel defaultSize={70} minSize={40}>
                  <div className="pr-2 h-full">
                    <ChatAgent sessionId={selectedId} />
                  </div>
                </ResizablePanel>
                <ResizableHandle withHandle />
                <ResizablePanel defaultSize={30} minSize={20}>
                  <div className="pl-2 h-full">
                    <SessionsPanel
                      sessions={sessions}
                      selectedId={selectedId}
                      onSelect={handleSelect}
                      onCreate={handleNew}
                    />
                  </div>
                </ResizablePanel>
              </ResizablePanelGroup>
            ) : (
              <ChatAgent sessionId={selectedId} />
            )}
          </div>
        </main>
      </div>
    </>
  );
};

export default Dashboard;
