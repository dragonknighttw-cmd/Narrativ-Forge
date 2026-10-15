"use client";

import { FormEvent, useEffect, useState } from "react";

const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

type Hook = { id: string; hook_text: string; hook_type: string; topic?: string; emotion?: string; used_count: number; views_average?: number; completion_average?: number; shares_average?: number; performance_score?: number; is_default: boolean };
type Log = { id: string; topic: string; category?: string; hook?: string; hook_type?: string; duration_seconds?: number; scene_count?: number; production_time_seconds?: number; quality_score?: number; published: boolean; platform?: string; views?: number; completion_rate?: number; shares?: number; saves?: number; notes?: string };
type Analytics = { manual_logs: number; published_logs: number; social_records: number; views: number; watch_time_seconds: number; shares: number; saves: number; comments: number; average_completion_rate: number; by_platform: { platform: string; records: number; views: number; shares: number; saves: number }[]; by_hook_type: { hook_type: string; logs: number; views: number }[] };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(base + path, { ...init, credentials: "include", headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) } });
  if (!r.ok) {
    let detail = "Request failed";
    try { const body = await r.json(); detail = typeof body.detail === "string" ? body.detail : body.detail?.message ?? detail; } catch {}
    throw new Error(detail);
  }
  return r.status === 204 ? (undefined as T) : r.json();
}

const hookTypes = ["question","shock","mystery","warning","personal_story","contrarian","cliffhanger"];

export default function ProductionIntelligencePage() {
  const [hooks, setHooks] = useState<Hook[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [hookText, setHookText] = useState("");
  const [hookType, setHookType] = useState("question");
  const [topic, setTopic] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    const [h, l, a] = await Promise.all([
      request<Hook[]>("/hooks"), request<Log[]>("/manual-production-logs"), request<Analytics>("/analytics"),
    ]);
    setHooks(h); setLogs(l); setAnalytics(a);
  }

  useEffect(() => { load().catch(e => setError(e.message)); }, []);

  async function addHook(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError("");
    try {
      await request("/hooks", { method: "POST", body: JSON.stringify({ hook_text: hookText, hook_type: hookType, topic: topic || null }) });
      setHookText(""); setTopic(""); await load();
    } catch (e) { setError(e instanceof Error ? e.message : "Failed"); } finally { setBusy(false); }
  }

  async function removeHook(id: string) {
    if (!confirm("Delete this hook?")) return;
    try { await request("/hooks/" + id, { method: "DELETE" }); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed"); }
  }

  return <main className="page">
    <div className="page-header"><div><h1>Production Intelligence</h1><p>Hooks, manual production records, and social performance. Defaults remain human-controlled.</p></div></div>
    {error && <div className="error">{error}</div>}

    {analytics && <section className="kpi-grid">
      <div className="kpi-card"><span>Views</span><strong>{analytics.views.toLocaleString()}</strong></div>
      <div className="kpi-card"><span>Completion</span><strong>{analytics.average_completion_rate.toFixed(1)}%</strong></div>
      <div className="kpi-card"><span>Shares</span><strong>{analytics.shares.toLocaleString()}</strong></div>
      <div className="kpi-card"><span>Production logs</span><strong>{analytics.manual_logs}</strong></div>
    </section>}

    <section className="card">
      <h2>Hook Library</h2>
      <form onSubmit={addHook} className="form-grid">
        <input aria-label="Hook text" value={hookText} onChange={e => setHookText(e.target.value)} placeholder="Hook text" required />
        <select aria-label="Hook type" value={hookType} onChange={e => setHookType(e.target.value)}>{hookTypes.map(x => <option key={x}>{x}</option>)}</select>
        <input aria-label="Topic" value={topic} onChange={e => setTopic(e.target.value)} placeholder="Topic (optional)" />
        <button className="primary" disabled={busy}>Add hook</button>
      </form>
      <div className="list">{hooks.map(h => <div className="list-row" key={h.id}>
        <div><strong>{h.hook_text}</strong><small>{h.hook_type} · used {h.used_count}×{h.is_default ? " · default" : ""}</small></div>
        {!h.is_default && <button className="text-button" onClick={() => removeHook(h.id)}>Delete</button>}
      </div>)}</div>
    </section>

    <section className="card">
      <h2>Manual Production Log</h2>
      <p className="muted">Use the episode workflow to record a production; this table exposes the saved production history.</p>
      <div className="table-wrap"><table><thead><tr><th>Topic</th><th>Hook</th><th>Duration</th><th>Quality</th><th>Published</th><th>Views</th></tr></thead>
      <tbody>{logs.map(l => <tr key={l.id}><td>{l.topic}</td><td>{l.hook_type ?? "—"}</td><td>{l.duration_seconds ?? "—"}s</td><td>{l.quality_score ?? "—"}</td><td>{l.published ? "Yes" : "No"}</td><td>{(l.views ?? 0).toLocaleString()}</td></tr>)}</tbody></table></div>
    </section>

    {analytics && <section className="card">
      <h2>Analytics</h2>
      <div className="table-wrap"><table><thead><tr><th>Platform</th><th>Records</th><th>Views</th><th>Shares</th><th>Saves</th></tr></thead>
      <tbody>{analytics.by_platform.map(x => <tr key={x.platform}><td>{x.platform}</td><td>{x.records}</td><td>{x.views.toLocaleString()}</td><td>{x.shares.toLocaleString()}</td><td>{x.saves.toLocaleString()}</td></tr>)}</tbody></table></div>
      <h3>Hook types</h3>
      <div className="table-wrap"><table><thead><tr><th>Hook type</th><th>Logs</th><th>Views</th></tr></thead>
      <tbody>{analytics.by_hook_type.map(x => <tr key={x.hook_type}><td>{x.hook_type}</td><td>{x.logs}</td><td>{x.views.toLocaleString()}</td></tr>)}</tbody></table></div>
    </section>}
  </main>;
}
