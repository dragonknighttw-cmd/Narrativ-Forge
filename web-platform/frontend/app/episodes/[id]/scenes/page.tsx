"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../../components/app-shell";
import { ErrorState } from "../../../../components/domain-forms";
import { api, Scene } from "../../../../lib/api";

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

  async function autoBreakdownFromScript() {
    setBusy(true); setError("");
    try {
      const scripts = await api.listScripts(id);
      const current = scripts.find(s => s.is_current) || scripts[0];
      if (!current || !current.content.trim()) {
        setError("No script found. Draft a script in Script Studio first.");
        return;
      }
      await api.autoPlanEpisode(id, { idea: current.content.slice(0, 500) });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Auto-breakdown failed");
    } finally {
      setBusy(false);
    }
  }

  const totalDuration = scenes.reduce((sum, s) => sum + (s.duration_seconds || 0), 0);

  return <AppShell title="Scene Breakdown">
    <section className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <div className="eyebrow">SCENES</div>
          <h2>Break the script into purposeful scenes</h2>
        </div>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <span style={{ fontSize: "0.875rem", padding: "0.25rem 0.75rem", borderRadius: "9999px", background: totalDuration >= 150 && totalDuration <= 210 ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.2)", color: totalDuration >= 150 && totalDuration <= 210 ? "#10b981" : "#f59e0b", fontWeight: 600 }}>
            Total: {totalDuration}s / 180s target
          </span>
          <button onClick={autoBreakdownFromScript} disabled={busy}>
            {busy ? "Analyzing…" : "⚡ Auto-Breakdown from Script"}
          </button>
        </div>
      </div>
      {error && <ErrorState message={error} retry={load} />}
      <div className="stack-form" style={{ marginTop: "1rem" }}>
        <input value={purpose} onChange={e => setPurpose(e.target.value)} placeholder="Scene purpose (e.g. hook, problem, detail, climax)" />
        <textarea className="burmese-text" value={description} onChange={e => setDescription(e.target.value)} placeholder="Visual direction (ရုပ်ထွက်ဖော်ပြချက်)" rows={3} />
        <textarea className="burmese-text" value={dialogue} onChange={e => setDialogue(e.target.value)} placeholder="Dialogue / narration (ပြောစကား / ဇာတ်ကြောင်းပြော)" rows={4} />
        <input type="number" min="1" value={duration} onChange={e => setDuration(e.target.value)} placeholder="Duration seconds" />
        <button className="primary" disabled={busy || !purpose.trim()} onClick={addScene}>Add scene</button>
      </div>
    </section>
    <section className="card">
      <div className="eyebrow">SCENE SEQUENCE ({scenes.length} scenes)</div>
      {scenes.length === 0 ? <div className="empty-state">No scenes yet. Click "⚡ Auto-Breakdown from Script" or add manually above.</div> : <div className="list">
        {scenes.map(scene => (
          <article className="list-card" key={scene.id}>
            <div>
              <strong>Scene {scene.scene_number}: {scene.purpose}</strong>
              <p className="muted">{scene.duration_seconds ?? "—"}s · {scene.description || "No visual direction"}</p>
              <p className="burmese-text" style={{ marginTop: "0.25rem" }}>{scene.dialogue || "No dialogue"}</p>
            </div>
          </article>
        ))}
      </div>}
    </section>
  </AppShell>;
}
