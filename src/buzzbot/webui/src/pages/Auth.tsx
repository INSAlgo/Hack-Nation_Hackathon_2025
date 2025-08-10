import { Helmet } from "react-helmet-async";
import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import logoUrl from "@/assets/buzzbot-logo.svg";

const Auth = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as any)?.from || "/app";
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const title = mode === "signin" ? "BuzzBot – Log in" : "BuzzBot – Sign up";
  const description = "Access BuzzBot to create better content with AI.";
  const canonical = typeof window !== "undefined" ? window.location.origin + "/auth" : "/auth";

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Replace with real Supabase auth. This is a temporary app gate.
    localStorage.setItem("buzzbot_auth", "1");
    navigate(from, { replace: true });
  };

  return (
    <div className="min-h-dvh grid grid-rows-[auto,1fr] bg-background">
      <Helmet>
        <title>{title}</title>
        <meta name="description" content={description} />
        <link rel="canonical" href={canonical} />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
      </Helmet>

      <header className="w-full border-b">
        <div className="container mx-auto flex items-center justify-between h-14 px-4">
          <Link to="/" className="flex items-center gap-2" aria-label="Go to BuzzBot Home">
            <img src={logoUrl} alt="BuzzBot logo" className="h-6 w-6" />
            <span className="text-sm font-medium">BuzzBot</span>
          </Link>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/">Home</Link>
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <div className="flex items-center gap-3">
              <img src={logoUrl} alt="BuzzBot" className="h-8 w-8" />
              <div>
                <CardTitle className="text-xl">{mode === "signin" ? "Welcome back" : "Create your account"}</CardTitle>
                <CardDescription>Use email and password to {mode === "signin" ? "log in" : "sign up"}.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full">
                {mode === "signin" ? "Log in" : "Create account"}
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {mode === "signin" ? "New to BuzzBot?" : "Already have an account?"}
            </p>
            <Button variant="link" className="px-0" onClick={() => setMode(mode === "signin" ? "signup" : "signin")}>{mode === "signin" ? "Sign up" : "Log in"}</Button>
          </CardFooter>
        </Card>
      </main>
    </div>
  );
};

export default Auth;
