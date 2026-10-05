"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "../../../lib/api";

function MagicLinkContent() {
  const router = useRouter();
  const params = useSearchParams();
  const token = params.get("token") ?? "";
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    if (!token) {
      setError("Magic-link token is missing.");
      return () => { active = false; };
    }
    api.consumeMagicLink(token)
      .then(() => router.replace("/dashboard"))
      .catch((e) => {
        if (active) setError(e instanceof Error ? e.message : "Magic link is invalid or expired.");
      });
    return () => { active = false; };
  }, [router, token]);

  return <main className="login">
    <section className="login-card">
      <div className="brand-mark">NF</div>
      <div className="eyebrow">NARRATIV FORGE</div>
      <h1>{error ? "Sign-in link unavailable" : "Signing you in…"}</h1>
      <p className="muted">{error || "Please wait while your secure session is created."}</p>
      {error && <button className="primary" onClick={() => router.replace("/login")}>Back to sign in</button>}
    </section>
  </main>;
}

export default function MagicLinkPage() {
  return (
    <Suspense fallback={<main className="login"><section className="login-card"><div className="brand-mark">NF</div><div className="eyebrow">NARRATIV FORGE</div><h1>Signing you in…</h1><p className="muted">Please wait while your secure session is created.</p></section></main>}>
      <MagicLinkContent />
    </Suspense>
  );
}
