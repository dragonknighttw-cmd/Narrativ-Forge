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
        // The legacy password endpoint is allowed only in disposable local E2E builds.
        // The explicit flag and loopback API check prevent this fallback from targeting production.
        const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "");
        const localE2EAuth = process.env.NEXT_PUBLIC_E2E_AUTH_MODE === "true"
          && apiBase === "http://localhost:8000/api/v1";
        if (process.env.NODE_ENV === "production" && !localE2EAuth) {
          throw new Error("Supabase Auth configuration is missing.");
        }
        if (process.env.NODE_ENV !== "production" || localE2EAuth) {
          await api.loginLegacy(email.trim(), password);
          router.replace("/dashboard");
          return;
        }
      }
      const authResponse = await fetch(`${supabaseUrl}/auth/v1/token?grant_type=password`, {
        method: "POST",
        headers: { apikey: supabaseKey, "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });
      if (!authResponse.ok) {
        if (authResponse.status === 400 || authResponse.status === 401) {
          throw new Error("Invalid email or password.");
        }
        if (authResponse.status === 429) {
          throw new Error("Too many sign-in attempts. Wait a moment and try again.");
        }
        throw new Error("Supabase Auth service is unavailable or misconfigured.");
      }
      const authSession = await authResponse.json() as { access_token?: string };
      if (!authSession.access_token) throw new Error("Supabase did not return a login session.");
      await api.loginWithSupabase(authSession.access_token);
      router.replace("/dashboard");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed.";
      if (message === "Supabase Auth configuration is missing." ||
          message === "Backend API configuration is missing." ||
          message === "Supabase Auth is not configured" ||
          message === "Initial Owner identity is not configured") {
        setError("Login configuration မပြည့်စုံသေးပါ။ Render ရဲ့ frontend/backend environment settings ကို စစ်ဆေးရန်လိုပါတယ်။");
      } else if (message === "Invalid email or password.") {
        setError("Email သို့မဟုတ် password မှားနေပါတယ်။ Supabase Auth မှာ အတည်ပြုထားတဲ့ account ကို သုံးပါ။");
      } else if (message === "Workspace membership required" ||
                 message === "Configured Owner workspace was not found" ||
                 message === "Owner account could not be provisioned safely" ||
                 message === "Account mapping conflict; contact the workspace owner") {
        setError("Supabase login အောင်မြင်ပေမယ့် workspace Owner ချိတ်ဆက်မှု မပြီးသေးပါ။ Account/database mapping ကို စစ်ဆေးရန်လိုပါတယ်။");
      } else if (message === "Too many sign-in attempts. Wait a moment and try again.") {
        setError("Login ကြိုးစားမှု များနေပါတယ်။ ခဏစောင့်ပြီး ပြန်ကြိုးစားပါ။");
      } else if (message === "Supabase Auth service is unavailable or misconfigured.") {
        setError("Supabase Auth service ကို ချိတ်ဆက်မရပါ။ Project URL, anon key နဲ့ Auth service status ကို စစ်ပါ။");
      } else if (message === "Supabase Auth is temporarily unavailable") {
        setError("Supabase Auth ကို backend က ချိတ်ဆက်မရပါ။ ခဏနေရင် ပြန်ကြိုးစားပါ။");
      } else {
        setError("Backend session ဖန်တီးမရပါ။ API URL, CORS နဲ့ backend logs ကို စစ်ဆေးရန်လိုပါတယ်။");
      }
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
