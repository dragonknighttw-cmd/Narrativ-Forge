"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../../components/app-shell";
import { ErrorState } from "../../../components/domain-forms";
import { api, Episode, ProcessingJob } from "../../../lib/api";

export default function ProcessingQueuePage() {
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [episodeId, setEpisodeId] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    try { setError(""); const [jobItems, episodeItems] = await Promise.all([api.listJobs(), api.listEpisodes()]); setJobs(jobItems); setEpisodes(episodeItems); if (!episodeId && episodeItems[0]) setEpisodeId(episodeItems[0].id); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to load processing queue"); }
  }
  useEffect(() => { load(); }, []);

  async function create() {
    if (!episodeId) return; setBusy(true); setError("");
    try { await api.createMockJob(episodeId); await load(); } catch (e) { setError(e instanceof Error ? e.message : "Failed to create processing job"); } finally { setBusy(false); }
  }

  return <AppShell title="Processing Queue">
    <section className="card"><div className="eyebrow">MOCK WORKER</div><h2>Verify processing workflow before real FFmpeg/Whisper</h2>{error && <ErrorState message={error} retry={load} />}
      <div className="inline-form"><select value={episodeId} onChange={e => setEpisodeId(e.target.value)} aria-label="Episode">{episodes.map(e => <option key={e.id} value={e.id}>{e.public_id} · {e.title}</option>)}</select><button className="primary" disabled={!episodeId || busy} onClick={create}>Run mock processing</button></div>
    </section>
    <section className="card">{jobs.length === 0 ? <div className="empty-state">No processing jobs yet.</div> : <div className="list">{jobs.map(job => <article className="list-card" key={job.id}><div><strong>{job.job_type}</strong><p className="muted">{job.status} · {job.progress}% · retries {job.retry_count}</p></div>{job.status === "failed" && <button className="text-button" onClick={async () => { await api.retryJob(job.id); await load(); }}>Retry</button>}</article>)}</div>}</section>
  </AppShell>;
}
