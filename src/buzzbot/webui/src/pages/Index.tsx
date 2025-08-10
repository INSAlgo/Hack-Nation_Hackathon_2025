import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Sparkles, Film, Hash, PlayCircle, CheckCircle2 } from "lucide-react";

const Index = () => {
  const title = "TikTok Igniter AI – Create Viral Videos";
  const description = "Professional AI for hooks, scripts, and captions. Build TikToks that feel extraordinary.";
  const canonical = typeof window !== "undefined" ? window.location.origin + "/" : "/";

  const jsonLdApp = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "TikTok Igniter AI",
    applicationCategory: "CreativeWorkApplication",
    description,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    url: canonical,
  };

  const jsonLdFaq = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: [
      {
        "@type": "Question",
        name: "What does TikTok Igniter AI generate?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "Hooks, scripts (15–30s), B-roll prompts, captions, and hashtags tailored to your niche.",
        },
      },
      {
        "@type": "Question",
        name: "Is it free to start?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "Yes, you can try it free. No credit card required to get started.",
        },
      },
      {
        "@type": "Question",
        name: "Can I preview content instantly?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "Yes. Generate your idea and preview the result immediately in the app.",
        },
      },
    ],
  };

  return (
    <>
      <Helmet>
        <title>{title}</title>
        <meta name="description" content={description} />
        <link rel="canonical" href={canonical} />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <script type="application/ld+json">{JSON.stringify(jsonLdApp)}</script>
        <script type="application/ld+json">{JSON.stringify(jsonLdFaq)}</script>
      </Helmet>

      <header className="w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span aria-label="brand" className="text-sm font-medium text-muted-foreground">
              TikTok Igniter AI
            </span>
          </div>
          <nav aria-label="primary">
            <ul className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
              <li><a href="#features" className="hover:text-foreground transition-colors">Features</a></li>
              <li><a href="#how" className="hover:text-foreground transition-colors">How it works</a></li>
              <li><a href="#showcase" className="hover:text-foreground transition-colors">Showcase</a></li>
              <li><a href="#faq" className="hover:text-foreground transition-colors">FAQ</a></li>
            </ul>
          </nav>
          <div className="flex items-center gap-3">
            <Button asChild variant="secondary" size="sm">
              <Link to="/app">Open App</Link>
            </Button>
          </div>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="relative overflow-hidden border-b">
          <div className="container py-20 md:py-28">
            <h1 className="text-4xl md:text-6xl font-semibold tracking-tight max-w-3xl leading-tight">
              Create viral TikToks with professional AI
            </h1>
            <p className="mt-6 text-lg md:text-xl text-muted-foreground max-w-2xl">
              Generate scroll-stopping hooks, tight scripts, B‑roll prompts, and captions — crafted to feel effortless.
            </p>
            <div className="mt-8 flex items-center gap-3">
              <Button asChild size="lg" variant="hero">
                <Link to="/app">Try the app</Link>
              </Button>
              <Button asChild size="lg" variant="outline">
                <a href="#how">See how it works</a>
              </Button>
            </div>
            <div className="mt-14 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <Feature icon={<Sparkles className="mr-2" />} title="Smart hooks" desc="Magnetic openings tailored to your niche." />
              <Feature icon={<Film className="mr-2" />} title="Script + B‑roll" desc="Beat-by-beat scripts with visual prompts." />
              <Feature icon={<Hash className="mr-2" />} title="Captions" desc="SEO-friendly captions and hashtags." />
              <Feature icon={<PlayCircle className="mr-2" />} title="Instant preview" desc="See it come alive instantly." />
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="container py-20 md:py-28">
          <div className="grid md:grid-cols-3 gap-10">
            <Card title="Human-grade tone" points={["Conversational hooks","Audience-first framing","Clear, concise beats"]} />
            <Card title="Built for speed" points={["One prompt to results","No fluff, just output","Preview on the spot"]} />
            <Card title="Consistent quality" points={["Opinionated templates","Best-practice structure","Refine with one click"]} />
          </div>
        </section>

        {/* How it works */}
        <section id="how" className="border-y">
          <div className="container py-20 md:py-28">
            <h2 className="text-2xl md:text-3xl font-semibold">How it works</h2>
            <ol className="mt-10 grid md:grid-cols-3 gap-8">
              <Step n={1} title="Describe your niche" text="Tell us the topic, vibe, and goal." />
              <Step n={2} title="Generate" text="Hooks, scripts, B‑roll, and captions in seconds." />
              <Step n={3} title="Preview & refine" text="See it instantly and tweak as needed." />
            </ol>
          </div>
        </section>

        {/* Showcase */}
        <section id="showcase" className="container py-20 md:py-28">
          <h2 className="text-2xl md:text-3xl font-semibold">Showcase</h2>
          <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1,2,3,4,5,6].map((i) => (
              <article key={i} className="rounded-lg border bg-card text-card-foreground overflow-hidden">
                <img
                  src="/placeholder.svg"
                  alt={`Sample TikTok concept ${i}`}
                  loading="lazy"
                  className="w-full aspect-[4/5] object-cover"
                />
                <div className="p-4">
                  <h3 className="text-sm font-medium">Concept {i}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">Hook + script + B‑roll prompts</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="border-t">
          <div className="container py-20 md:py-28">
            <h2 className="text-2xl md:text-3xl font-semibold">Frequently asked questions</h2>
            <div className="mt-8">
              <Accordion type="single" collapsible className="w-full">
                <AccordionItem value="item-1">
                  <AccordionTrigger>What makes the hooks effective?</AccordionTrigger>
                  <AccordionContent>
                    We combine pattern interrupts, specificity, and narrative tension to stop the scroll.
                  </AccordionContent>
                </AccordionItem>
                <AccordionItem value="item-2">
                  <AccordionTrigger>Will my videos feel generic?</AccordionTrigger>
                  <AccordionContent>
                    No. Prompts are tailored to your niche and tone, with simple controls to refine style.
                  </AccordionContent>
                </AccordionItem>
                <AccordionItem value="item-3">
                  <AccordionTrigger>Can I use it without video editing skills?</AccordionTrigger>
                  <AccordionContent>
                    Yes. Each script includes clear beats and B‑roll ideas so you can record quickly.
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="container py-16 md:py-24">
          <div className="rounded-2xl border bg-gradient-to-b from-background to-muted/30 p-8 md:p-12 text-center">
            <h2 className="text-2xl md:text-3xl font-semibold">Ship your next TikTok in minutes</h2>
            <p className="mt-3 text-muted-foreground">Start free. No credit card required.</p>
            <div className="mt-6">
              <Button asChild size="lg" variant="hero">
                <Link to="/app">Open the app</Link>
              </Button>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t">
        <div className="container h-16 flex items-center justify-between text-sm text-muted-foreground">
          <span>© {new Date().getFullYear()} TikTok Igniter AI</span>
          <a href="#top" className="hover:text-foreground">Back to top</a>
        </div>
      </footer>
    </>
  );
};

function Feature({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="flex items-start">
      <div className="mt-1 text-primary">{icon}</div>
      <div>
        <p className="font-medium">{title}</p>
        <p className="text-sm text-muted-foreground">{desc}</p>
      </div>
    </div>
  );
}

function Card({ title, points }: { title: string; points: string[] }) {
  return (
    <article className="rounded-xl border p-6 bg-card text-card-foreground">
      <h3 className="font-medium">{title}</h3>
      <ul className="mt-4 space-y-2 text-sm">
        {points.map((p) => (
          <li key={p} className="flex items-start gap-2"><CheckCircle2 className="mt-0.5 h-4 w-4 text-primary" />{p}</li>
        ))}
      </ul>
    </article>
  );
}

function Step({ n, title, text }: { n: number; title: string; text: string }) {
  return (
    <li className="rounded-xl border p-6 bg-card text-card-foreground">
      <div className="flex items-center gap-3">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">{n}</span>
        <p className="font-medium">{title}</p>
      </div>
      <p className="mt-3 text-sm text-muted-foreground">{text}</p>
    </li>
  );
}

export default Index;
