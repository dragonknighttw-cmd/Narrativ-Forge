"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL?.replace(/\/+$/, "");
      const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
      if (!supabaseUrl || !supabaseKey) {
        throw new Error("Supabase Auth configuration is missing.");
      }
      const authResponse = await fetch(`${supabaseUrl}/auth/v1/token?grant_type=password`, {
        method: "POST",
        headers: { apikey: supabaseKey, "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });
      if (!authResponse.ok) throw new Error("Invalid email or password.");
      const authSession = await authResponse.json() as { access_token?: string };
      if (!authSession.access_token) throw new Error("Supabase did not return a login session.");
      await api.loginWithSupabase(authSession.access_token);
      router.replace("/dashboard");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed.";
      setError(message === "Supabase Auth configuration is missing."
        ? "Login configuration is incomplete. Contact the workspace administrator."
        : "Login မအောင်မြင်ပါ။ Supabase email/password သို့မဟုတ် backend connection ကို စစ်ပါ။");
    } finally {
      setBusy(false);
    }
  }

  return <main className="login">
    <form className="login-card" onSubmit={submit}>
      <div className="brand-mark">NF</div>
      <div className="eyebrow">NARRATIV FORGE</div>
      <h1>Production workspace</h1>
      <p className="muted">Invite-only access. Authentication is managed by Supabase; app sessions use an httpOnly cookie.</p>
      <label className="field">Email<input required type="email" autoComplete="username" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} /></label>
      <label className="field">Password<input required autoComplete="current-password" placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} /></label>
      {error && <div className="error" role="alert">{error}</div>}
      <button className="primary" type="submit" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
    </form>
  </main>;
}
