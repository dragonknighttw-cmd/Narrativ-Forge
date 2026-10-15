"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";
import { api, Episode, ProcessingJob } from "../../lib/api";

export default function ProcessingQueuePage() {
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [episodeId, setEpisodeId] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    try {
      setError("");
      const [jobItems, episodeItems] = await Promise.all([api.listJobs(), api.listEpisodes()]);
      setJobs(jobItems);
      setEpisodes(episodeItems);
      if (!episodeId && episodeItems[0]) setEpisodeId(episodeItems[0].id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load processing queue");
    }
  }

  useEffect(() => {
    load();
    const timer = window.setInterval(() => { void load(); }, 3000);
    return () => window.clearInterval(timer);
  }, []);

  async function createReal() {
    if (!episodeId) return;
    setBusy(true);
    setError("");
    try {
      await api.createRealJob(episodeId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create processing job");
    } finally {
      setBusy(false);
    }
  }

  async function createMock() {
    if (!episodeId) return;
    setBusy(true);
    setError("");
    try {
      await api.createMockJob(episodeId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create mock processing job");
    } finally {
      setBusy(false);
    }
  }

  const [statusFilter, setStatusFilter] = useState("all");

  const filteredJobs = jobs.filter(j => {
    if (statusFilter === "running") return j.status === "queued" || j.status === "running";
    if (statusFilter === "completed") return j.status === "completed";
    if (statusFilter === "failed") return j.status === "failed";
    return true;
  });

  const STEPS = [
    { title: "Queued", desc: "Broker enqueue (Redis)", status: "queued" },
    { title: "Audio Extract", desc: "FFmpeg 16kHz mono normalization", status: "running" },
    { title: "Whisper ASR", desc: "Burmese Speech-to-Text inference", status: "running" },
    { title: "Subtitles", desc: "VTT/SRT timing & Unicode check", status: "running" },
    { title: "Completed", desc: "Assets persisted for Review", status: "completed" },
  ];

  return (
    <AppShell title="Processing Queue">
      <section className="card">
        <div className="eyebrow">PROCESSING STATE MACHINE</div>
        <h2>Media Pipeline Lifecycle Stepper</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.75rem", marginTop: "1rem" }}>
          {STEPS.map((s, idx) => (
            <div key={idx} style={{ padding: "0.75rem", borderRadius: "6px", background: "#0f172a", border: "1px solid #334155" }}>
              <div style={{ fontSize: "0.75rem", color: "#6366f1", fontWeight: 700 }}>STAGE {idx + 1}</div>
              <strong style={{ fontSize: "0.9rem", display: "block", marginTop: "0.2rem" }}>{s.title}</strong>
              <p className="muted" style={{ fontSize: "0.75rem", margin: "0.25rem 0 0" }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <div className="eyebrow">PROCESSING WORKER DISPATCH</div>
        <h2>Trigger Background Job</h2>
        <p className="muted">Run real FFmpeg + Whisper on background worker or execute deterministic mock processing for rapid development.</p>
        {error && <ErrorState message={error} retry={load} />}
        <div className="inline-form" style={{ flexWrap: "wrap", gap: "0.75rem" }}>
          <select value={episodeId} onChange={e => setEpisodeId(e.target.value)} aria-label="Episode" style={{ minWidth: "240px" }}>
            {episodes.map(e => <option key={e.id} value={e.id}>{e.public_id} · {e.title}</option>)}
          </select>
          <div className="inline-form" style={{ gap: "0.5rem" }}>
            <button className="primary" disabled={!episodeId || busy} onClick={createReal}>
              {busy ? "Dispatching…" : "Dispatch Real Worker"}
            </button>
            <button className="text-button" disabled={!episodeId || busy} onClick={createMock}>
              Run Mock Processing (Instant)
            </button>
          </div>
        </div>
      </section>

      <section className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
          <div className="eyebrow">JOBS ({filteredJobs.length} / {jobs.length})</div>
          <div style={{ display: "flex", gap: "0.35rem" }}>
            {["all", "running", "completed", "failed"].map(tab => (
              <button
                key={tab}
                className={statusFilter === tab ? "primary" : "text-button"}
                style={{ padding: "0.25rem 0.6rem", fontSize: "0.8rem", textTransform: "capitalize" }}
                onClick={() => setStatusFilter(tab)}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {filteredJobs.length === 0 ? (
          <div className="empty-state" style={{ marginTop: "1rem" }}>
            No {statusFilter === "all" ? "" : statusFilter} jobs in queue. Select an episode above to start processing.
          </div>
        ) : (
          <div className="list" style={{ marginTop: "1rem" }}>
            {filteredJobs.map(job => (
              <article className="list-card" key={job.id} style={{ display: "block", padding: "1rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <strong>{job.job_type.toUpperCase()} · #{job.id.slice(0, 8)}</strong>
                      <span className="pill" style={{
                        background: job.status === "completed" ? "rgba(16,185,129,0.15)" : job.status === "failed" ? "rgba(239,68,68,0.15)" : "rgba(99,102,241,0.15)",
                        color: job.status === "completed" ? "#10b981" : job.status === "failed" ? "#ef4444" : "#6366f1",
                        fontSize: "0.75rem",
                      }}>
                        {job.status}
                      </span>
                    </div>
                    <p className="muted" style={{ margin: "0.25rem 0 0", fontSize: "0.85rem" }}>
                      Episode: {job.episode_id.slice(0, 8)} · Retries: {job.retry_count} · Progress: {job.progress}%
                    </p>
                  </div>
                  {job.status === "failed" && (
                    <button
                      className="text-button"
                      style={{ color: "#ef4444" }}
                      onClick={async () => { await api.retryJob(job.id); await load(); }}
                    >
                      Retry Job
                    </button>
                  )}
                </div>

                {/* Live Progress Bar */}
                <div style={{ width: "100%", height: "6px", background: "#1e293b", borderRadius: "9999px", marginTop: "0.75rem", overflow: "hidden" }}>
                  <div style={{
                    width: `${job.progress}%`,
                    height: "100%",
                    background: job.status === "completed" ? "#10b981" : job.status === "failed" ? "#ef4444" : "#6366f1",
                    transition: "width 0.3s ease",
                  }} />
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </AppShell>
  );
}
