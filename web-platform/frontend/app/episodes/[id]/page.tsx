"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../components/app-shell";
import { ErrorState } from "../../../components/domain-forms";
import { api, Episode } from "../../../lib/api";

const statuses = ["idea", "planned", "script_draft", "script_review", "assets_needed", "in_production", "processing", "subtitle_review", "needs_approval", "approved", "exporting", "exported", "archived", "rejected", "failed"];

export default function EpisodeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [item, setItem] = useState<Episode | null>(null);
  const [nextStatus, setNextStatus] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editDuration, setEditDuration] = useState("180");
  const [editing, setEditing] = useState(false);

  async function load() {
    try {
      setError("");
      const value = await api.getEpisode(id);
      setItem(value);
      setNextStatus("");
      setEditTitle(value.title);
      setEditDuration(String(value.target_duration_seconds));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load episode");
    }
  }

  useEffect(() => {
    if (id) load();
  }, [id]);

  async function transition() {
    if (!item || !nextStatus) return;
    setBusy(true);
    setError("");
    try {
      await api.updateEpisode(item.id, { status: nextStatus });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Status transition failed");
    } finally {
      setBusy(false);
    }
  }

  async function saveEpisode() {
    if (!item) return;
    setBusy(true);
    setError("");
    try {
      await api.updateEpisode(item.id, {
        title: editTitle.trim(),
        target_duration_seconds: Number(editDuration),
      });
      setEditing(false);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to update episode");
    } finally {
      setBusy(false);
    }
  }

  if (!item && error) {
    return <AppShell title="Episode"><ErrorState message={error} retry={load} /></AppShell>;
  }

  return (
    <AppShell title={item?.title || "Episode detail"}>
      {error && <ErrorState message={error} retry={load} />}
      {item && (
        <>
          <section className="card">
            <div className="eyebrow">{item.public_id}</div>
            <h2>{item.title}</h2>
            <p className="muted">Target duration: {item.target_duration_seconds}s · Current step: {item.current_step}</p>
            <span className="pill">{item.status}</span>
            {editing ? (
              <div className="stack-form">
                <input value={editTitle} onChange={e => setEditTitle(e.target.value)} aria-label="Episode title" />
                <input type="number" min="1" value={editDuration} onChange={e => setEditDuration(e.target.value)} aria-label="Target duration seconds" />
                <div className="inline-form">
                  <button className="primary" disabled={busy || !editTitle.trim()} onClick={saveEpisode}>Save</button>
                  <button className="text-button" onClick={() => setEditing(false)}>Cancel</button>
                </div>
              </div>
            ) : (
              <button className="text-button" onClick={() => setEditing(true)}>Edit episode</button>
            )}
          </section>

          <section className="card">
            <div className="eyebrow">PRODUCTION WORKSPACES</div>
            <div className="inline-form">
              <a className="text-button" href={`/episodes/${id}/script`}>Script Studio</a>
              <a className="text-button" href={`/episodes/${id}/scenes`}>Scene Breakdown</a>
              <a className="text-button" href={`/episodes/${id}/assets`}>Asset Library</a>
              <a className="text-button" href={`/episodes/${id}/subtitle`}>Subtitle Studio</a>
            </div>
          </section>

          <section className="card">
            <div className="eyebrow">STATUS TRANSITION</div>
            <h2>Move episode forward</h2>
            <p className="muted">Only transitions allowed by the workflow state machine are accepted by the backend.</p>
            <div className="inline-form">
              <select value={nextStatus} onChange={e => setNextStatus(e.target.value)} aria-label="Next status">
                <option value="">Select next status</option>
                {statuses.map(status => <option key={status} value={status}>{status}</option>)}
              </select>
              <button className="primary" disabled={!nextStatus || busy} onClick={transition}>{busy ? "Updating…" : "Update status"}</button>
            </div>
          </section>
        </>
      )}
    </AppShell>
  );
}
