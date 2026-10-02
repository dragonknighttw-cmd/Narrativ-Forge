"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../../../components/app-shell";
import { ErrorState } from "../../../../../components/domain-forms";
import { api, Scene } from "../../../../../lib/api";

export default function SceneBreakdownPage() {
  const { id } = useParams<{ id: string }>();
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [purpose, setPurpose] = useState("");
  const [description, setDescription] = useState("");
  const [dialogue, setDialogue] = useState("");
  const [duration, setDuration] = useState("10");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() { try { setError(""); setScenes(await api.listScenes(id)); } catch (e) { setError(e instanceof Error ? e.message : "Failed to load scenes"); } }
  useEffect(() => { if (id) load(); }, [id]);

  async function addScene() {
    setBusy(true); setError("");
    try {
      await api.createScene(id, { scene_number: scenes.length + 1, purpose: purpose.trim(), description: description.trim() || undefined, dialogue: dialogue.trim() || undefined, duration_seconds: Number(duration) });
      setPurpose(""); setDescription(""); setDialogue(""); await load();
    } catch (e) { setError(e instanceof Error ? e.message : "Failed to create scene"); } finally { setBusy(false); }
  }

  return <AppShell title="Scene Breakdown">
    <section className="card"><div className="eyebrow">SCENES</div><h2>Break the script into purposeful scenes</h2>{error && <ErrorState message={error} retry={load} />}
      <div className="stack-form"><input value={purpose} onChange={e => setPurpose(e.target.value)} placeholder="Scene purpose" /><textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="Visual direction" rows={3} /><textarea value={dialogue} onChange={e => setDialogue(e.target.value)} placeholder="Dialogue / narration" rows={4} /><input type="number" min="1" value={duration} onChange={e => setDuration(e.target.value)} placeholder="Duration seconds" /><button className="primary" disabled={busy || !purpose.trim()} onClick={addScene}>Add scene</button></div>
    </section>
    <section className="card">{scenes.length === 0 ? <div className="empty-state">No scenes yet.</div> : <div className="list">{scenes.map(scene => <article className="list-card" key={scene.id}><div><strong>Scene {scene.scene_number}: {scene.purpose}</strong><p className="muted">{scene.duration_seconds ?? "—"}s · {scene.description || "No visual direction"}</p><p>{scene.dialogue || "No dialogue"}</p></div></article>)}</div>}</section>
  </AppShell>;
}
