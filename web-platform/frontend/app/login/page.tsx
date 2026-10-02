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
      await api.login(email.trim(), password);
      router.replace("/dashboard");
    } catch {
      setError("Login မအောင်မြင်ပါ။ Email/password သို့မဟုတ် backend connection ကို စစ်ပါ။");
    } finally {
      setBusy(false);
    }
  }

  return <main className="login">
    <form className="login-card" onSubmit={submit}>
      <div className="brand-mark">NF</div>
      <div className="eyebrow">NARRATIV FORGE</div>
      <h1>Production workspace</h1>
      <p className="muted">Invite-only access. Session credentials are kept in an httpOnly cookie.</p>
      <label className="field">Email<input required autoComplete="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} /></label>
      <label className="field">Password<input required autoComplete="current-password" placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} /></label>
      {error && <div className="error" role="alert">{error}</div>}
      <button className="primary" type="submit" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
    </form>
  </main>;
}
