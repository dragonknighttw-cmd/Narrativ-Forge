"use client";
import { FormEvent, useState } from "react";
const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(base + path, { ...init, credentials: "include", headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) } });
  if (!r.ok) { let detail = "Request failed"; try { const b = await r.json(); detail = typeof b.detail === "string" ? b.detail : b.detail?.message ?? detail; } catch {} throw new Error(detail); }
  return r.json();
}
export default function AutoModePage() {
  const [episodeId, setEpisodeId] = useState(""); const [idea, setIdea] = useState("");
  const [result, setResult] = useState<any>(null); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function run(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError(""); setResult(null);
    try { const data = await request<any>("/auto/episodes/" + episodeId + "/run", { method: "POST", body: JSON.stringify({ idea }) }); setResult(data); }
    catch (err) { setError(err instanceof Error ? err.message : "Auto Mode failed"); } finally { setBusy(false); }
  }
  return <main className="page">
    <div className="page-header"><div><h1>Auto Mode</h1><p>Generate a draft plan, then continue through processing. Human review remains mandatory.</p></div></div>
    <section className="card"><form onSubmit={run} className="form-grid">
      <input value={episodeId} onChange={e => setEpisodeId(e.target.value)} placeholder="Episode ID" aria-label="Episode ID" required />
      <input value={idea} onChange={e => setIdea(e.target.value)} placeholder="Content idea" aria-label="Content idea" required />
      <button className="primary" disabled={busy}>{busy ? "Starting…" : "Start Auto Mode"}</button>
    </form>
    {error && <div className="error" role="alert">{error}</div>}
    {result && <div className="success" role="status"><strong>Auto Mode started</strong><p>Script: {result.script_id}</p><p>Scenes: {result.scene_count}</p><p>Processing job: {result.job_id}</p><p>Pipeline: {result.next_steps.join(" → ")}</p><p>Human review required: Yes</p></div>}
    </section></main>;
}