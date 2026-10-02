"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../../../components/app-shell";
import { ErrorState } from "../../../../../components/domain-forms";
import { api, Script } from "../../../../../lib/api";

export default function ScriptStudioPage() {
  const { id } = useParams<{ id: string }>();
  const [scripts, setScripts] = useState<Script[]>([]);
  const [content, setContent] = useState("");
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() { try { setError(""); setScripts(await api.listScripts(id)); } catch (e) { setError(e instanceof Error ? e.message : "Failed to load scripts"); } }
  useEffect(() => { if (id) load(); }, [id]);

  async function save(version: boolean) {
    setBusy(true); setError("");
    try {
      if (version) await api.createScriptVersion(id, { title: title || undefined, content });
      else await api.createScript(id, { title: title || undefined, content });
      setContent(""); setTitle(""); await load();
    } catch (e) { setError(e instanceof Error ? e.message : "Failed to save script"); } finally { setBusy(false); }
  }

  return <AppShell title="Script Studio">
    <section className="card">
      <div className="eyebrow">SCRIPT WORKFLOW</div><h2>Draft and version the episode script</h2>
      <p className="muted">AI drafts remain drafts; human editing is represented by explicit script versions.</p>
      {error && <ErrorState message={error} retry={load} />}
      <div className="stack-form"><input value={title} onChange={e => setTitle(e.target.value)} placeholder="Script title" /><textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Write the Burmese script…" rows={14} /><div className="inline-form"><button className="primary" disabled={busy} onClick={() => save(false)}>Create script</button><button disabled={busy || !content.trim()} onClick={() => save(true)}>Save new version</button></div></div>
    </section>
    <section className="card"><div className="eyebrow">VERSIONS</div>{scripts.length === 0 ? <div className="empty-state">No script versions yet.</div> : <div className="list">{scripts.map(s => <article className="list-card" key={s.id}><div><strong>v{s.version} {s.title || "Untitled"}</strong><p className="muted">{s.status} · {s.is_current ? "current" : "archived version"}</p></div><button className="text-button" onClick={() => { setTitle(s.title || ""); setContent(s.content); }}>Load</button></article>)}</div>}</section>
  </AppShell>;
}
