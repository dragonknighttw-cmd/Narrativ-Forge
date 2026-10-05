"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../../components/app-shell";
import { ErrorState } from "../../../../components/domain-forms";
import { api, Script } from "../../../../lib/api";

export default function ScriptStudioPage() {
  const { id } = useParams<{ id: string }>();
  const [scripts, setScripts] = useState<Script[]>([]);
  const [active, setActive] = useState<Script | null>(null);
  const [content, setContent] = useState("");
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [saveState, setSaveState] = useState<"saved" | "dirty" | "saving" | "conflict">("saved");
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  async function load() {
    try {
      setError("");
      const result = await api.listScripts(id);
      setScripts(result);
      if (active) {
        const current = result.find(item => item.id === active.id);
        if (current) {
          setActive(current);
          setSaveState("saved");
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load scripts");
    }
  }

  useEffect(() => {
    if (id) load();
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, [id]);

  async function createNew(version: boolean) {
    if (!content.trim() && version) return;
    setBusy(true);
    setError("");
    try {
      const created = version
        ? await api.createScriptVersion(id, { title: title || undefined, content })
        : await api.createScript(id, { title: title || undefined, content });
      setScripts(current => [created, ...current.filter(item => item.id !== created.id)]);
      setActive(created);
      setTitle(created.title || "");
      setContent(created.content);
      setSaveState("saved");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save script");
    } finally {
      setBusy(false);
    }
  }

  function selectScript(script: Script) {
    setActive(script);
    setTitle(script.title || "");
    setContent(script.content);
    setSaveState("saved");
    setError("");
  }

  async function autosave() {
    if (!active?.is_current || saveState === "saving") return;
    setSaveState("saving");
    try {
      const updated = await api.updateScript(id, active.id, {
        title: title || undefined,
        content,
        expected_row_version: active.row_version,
      });
      setActive(updated);
      setScripts(current => current.map(item => item.id === updated.id ? updated : item));
      setSaveState("saved");
      setError("");
    } catch (e) {
      setSaveState("conflict");
      setError(e instanceof Error ? e.message : "Autosave failed");
    }
  }

  useEffect(() => {
    if (!active?.is_current) return;
    setSaveState("dirty");
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => void autosave(), 900);
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, [content, title, active?.id]);

  return <AppShell title="Script Studio">
    <section className="card">
      <div className="eyebrow">SCRIPT WORKFLOW</div>
      <h2>Draft and version the episode script</h2>
      <p className="muted">Current scripts autosave with optimistic locking. Historical versions remain immutable.</p>
      {error && <ErrorState message={error} retry={load} />}
      <div className="stack-form">
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Script title" />
        <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Write the Burmese script…" rows={14} />
        <div className="inline-form">
          <button className="primary" disabled={busy || !!active} onClick={() => createNew(false)}>Create script</button><button disabled={busy} onClick={() => { setActive(null); setTitle(""); setContent(""); setSaveState("saved"); setError(""); }}>New draft</button>
          <button disabled={busy || !content.trim()} onClick={() => createNew(true)}>Save new version</button>
          {active?.is_current && <span className="muted">{saveState === "saving" ? "Saving…" : saveState === "dirty" ? "Unsaved changes…" : saveState === "conflict" ? "Conflict — reload before continuing" : "Saved"}</span>}
        </div>
      </div>
    </section>
    <section className="card">
      <div className="eyebrow">VERSIONS</div>
      {scripts.length === 0 ? <div className="empty-state">No script versions yet.</div> : <div className="list">
        {scripts.map(s => <article className="list-card" key={s.id}>
          <div><strong>v{s.version} {s.title || "Untitled"}</strong><p className="muted">{s.status} · {s.is_current ? "current" : "archived version"}</p></div>
          <button className="text-button" onClick={() => selectScript(s)}>Load</button>
        </article>)}
      </div>}
    </section>
  </AppShell>;
}
