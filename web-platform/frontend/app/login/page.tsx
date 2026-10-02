"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const result = await api.login(email, password);
      localStorage.setItem("nf_session", result.access_token);
      router.push("/dashboard");
    } catch {
      setError("Login မအောင်မြင်ပါ။ Backend ကို run ထားပြီး credentials ကို စစ်ပါ။");
    }
  }

  return <main className="login">
    <form className="login-card" onSubmit={submit}>
      <div className="brand-mark">NF</div>
      <div className="eyebrow">NARRATIV FORGE</div>
      <h1>Production workspace</h1>
      <p className="muted">Invite-only access</p>
      <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      {error && <div className="error">{error}</div>}
      <button className="primary" type="submit">Sign in</button>
    </form>
  </main>;
}