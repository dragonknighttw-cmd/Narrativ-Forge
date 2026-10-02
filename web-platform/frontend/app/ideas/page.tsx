"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";
import { api, Idea } from "../../lib/api";

export default function IdeasPage() {
  const [items, setItems] = useState<Idea[]>([]);
  const [title, setTitle] = useState("");
  const [concept, setConcept] = useState("");
  const [editing, setEditing] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editConcept, setEditConcept] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function load() { try { setError(""); setItems(await api.listIdeas()); } catch (e) { setError(e instanceof Error ? e.message : "Failed to load ideas"); } }
  useEffect(() => { load(); }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault(); if (!title.trim()) return; setBusy(true); setError("");
    try { await api.createIdea({ title: title.trim(), concept: concept.trim() || undefined }); setTitle(""); setConcept(""); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to create idea"); } finally { setBusy(false); }
  }
  function startEdit(item: Idea) { setEditing(item.id); setEditTitle(item.title); setEditConcept(item.concept || ""); }
  async function saveEdit() {
    if (!editing || !editTitle.trim()) return; setBusy(true); setError("");
    try { await api.updateIdea(editing, { title: editTitle.trim(), concept: editConcept.trim() || null }); setEditing(null); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to update idea"); } finally { setBusy(false); }
  }

  return <AppShell title="Ideas">
    <section className="card"><div className="eyebrow">STAGE 1 · IDEAS</div><h2>Capture the story seed</h2><p className="muted">Topic, concept and hook belong here before structure is created.</p>
      <form className="stack-form" onSubmit={add}><input required maxLength={255} placeholder="Idea title" value={title} onChange={e => setTitle(e.target.value)} /><textarea placeholder="Concept / short premise" value={concept} onChange={e => setConcept(e.target.value)} /><button className="primary" disabled={busy}>{busy ? "Saving…" : "Add idea"}</button></form>
    </section>
    {error && <ErrorState message={error} retry={load} />}
    {!error && !items.length && <section className="empty-state"><h3>No ideas yet</h3><p className="muted">Create the first story seed above.</p></section>}
    <div className="list">{items.map(item => editing === item.id
      ? <article className="card" key={item.id}><div className="stack-form"><input value={editTitle} onChange={e => setEditTitle(e.target.value)} /><textarea value={editConcept} onChange={e => setEditConcept(e.target.value)} /><div className="inline-form"><button className="primary" disabled={busy} onClick={saveEdit}>Save</button><button className="text-button" onClick={() => setEditing(null)}>Cancel</button></div></div></article>
      : <article className="card list-item" key={item.id}><div><div className="eyebrow">{item.status}</div><h3>{item.title}</h3><p className="muted">{item.concept || "No concept added yet."}</p></div><div><span className="pill">{item.category || "Uncategorized"}</span><button className="text-button" onClick={() => startEdit(item)}>Edit</button></div></article>)}</div>
  </AppShell>;
}
