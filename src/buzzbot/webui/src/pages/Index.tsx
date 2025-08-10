import { Helmet } from "react-helmet-async";
import ChatAgent from "@/components/dashboard/ChatAgent";
import VideoPanel from "@/components/dashboard/VideoPanel";

const Index = () => {
  const title = "TikTok Igniter AI – Viral Video Generator";
  const description = "Create viral TikTok hooks, scripts, and captions with AI, then preview instantly.";
  const canonical = typeof window !== "undefined" ? window.location.origin : "/";

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "TikTok Igniter AI",
    applicationCategory: "CreativeWorkApplication",
    description,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    url: canonical,
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
      <header className="h-14 w-full border-b bg-background px-4 flex items-center">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-muted-foreground">TikTok Igniter AI</span>
        </div>
      </header>

      {/* Main layout: chat + side video */}
      <div className="flex min-h-[calc(100dvh-3.5rem)] w-full overflow-hidden">
        <aside className="hidden lg:block w-[380px] xl:w-[420px] p-4 overflow-auto" aria-label="Video panel">
          <VideoPanel />
        </aside>
        <main className="flex-1 overflow-hidden p-4" aria-label="AI chat">
          <h1 className="sr-only">Create Viral TikToks with AI</h1>
          <div className="h-full">
            <ChatAgent />
          </div>
        </main>
      </div>
    </>
  );
};

export default Index;
