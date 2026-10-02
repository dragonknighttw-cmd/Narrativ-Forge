"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";
import { api, Series } from "../../lib/api";

export default function SeriesPage() {
  const [items, setItems] = useState<Series[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function load() { try { setError(""); setItems(await api.listSeries()); } catch (e) { setError(e instanceof Error ? e.message : "Failed to load series"); } }
  useEffect(() => { load(); }, []);
  async function add(e: React.FormEvent) {
    e.preventDefault(); if (!title.trim()) return;
    setBusy(true); setError("");
    try { await api.createSeries({ title: title.trim(), description: description.trim() || undefined }); setTitle(""); setDescription(""); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to create series"); } finally { setBusy(false); }
  }

  return <AppShell title="Series">
    <section className="card"><div className="eyebrow">STAGE 2 · STRUCTURE</div><h2>Series workspace</h2><p className="muted">Organize a story into seasons and ordered episodes.</p>
      <form className="stack-form" onSubmit={add}><input required maxLength={255} placeholder="Series title" value={title} onChange={e => setTitle(e.target.value)} /><textarea placeholder="Series description" value={description} onChange={e => setDescription(e.target.value)} /><button className="primary" disabled={busy}>{busy ? "Saving…" : "Create series"}</button></form>
    </section>
    {error && <ErrorState message={error} retry={load} />}
    {!error && !items.length && <section className="empty-state"><h3>No series yet</h3><p className="muted">Create a series to start seasons and episodes.</p></section>}
    <div className="grid">{items.map(item => <Link href={"/series/" + item.id} className="card list-item" key={item.id}><div><div className="eyebrow">{item.status}</div><h3>{item.title}</h3><p className="muted">{item.description || "No description yet."}</p></div><span>Open →</span></Link>)}</div>
  </AppShell>;
}
