"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "../../lib/api";

export default function InvitePage() {
  const params = useSearchParams();
  const router = useRouter();
  const token = params.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (!token) throw new Error("Invitation token is missing or expired.");
      await api.acceptInvitation(token, password);
      router.replace("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invitation could not be accepted.");
    } finally {
      setBusy(false);
    }
  }

  return <main className="login">
    <form className="login-card" onSubmit={submit}>
      <div className="brand-mark">NF</div>
      <div className="eyebrow">NARRATIV FORGE</div>
      <h1>Join workspace</h1>
      <p className="muted">Set your password to accept the invitation.</p>
      <label className="field">Password<input required minLength={12} type="password" autoComplete="new-password" value={password} onChange={e => setPassword(e.target.value)} /></label>
      {error && <div className="error" role="alert">{error}</div>}
      <button className="primary" disabled={busy || !token}>{busy ? "Joining…" : "Accept invitation"}</button>
    </form>
  </main>;
}
