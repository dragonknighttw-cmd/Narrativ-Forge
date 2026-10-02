"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../../components/app-shell";
import { ErrorState } from "../../../components/domain-forms";

const CHECKS = ["video_watched", "audio_checked", "subtitle_timing_checked", "thumbnail_present"] as const;

export default function ReviewCenterPage({ params }: { params: { id: string } }) {
  const id = params.id;
  const [review, setReview] = useState<any>(null);
  const [checks, setChecks] = useState<Record<string, boolean>>({
    video_watched: false, audio_checked: false, subtitle_timing_checked: false, thumbnail_present: false
  });
  const [issues, setIssues] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    try {
      const response = await fetch("/api/v1/episodes/" + id + "/review", { credentials: "include" });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Review load failed");
      setReview(body); setChecks(body.checklist);
    } catch (e) { setError(e instanceof Error ? e.message : "Review load failed"); }
  }
  useEffect(() => { load(); }, [id]);

  async function action(path: string) {
    setBusy(true); setError(""); setMessage("");
    try {
      const response = await fetch("/api/v1/episodes/" + id + "/review" + path, {
        method: "POST", credentials: "include", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...checks, critical_issues: issues.split("\n").filter(Boolean), notes })
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail?.message ?? body.detail ?? "Review action failed");
      setMessage(path === "/approve" ? "Episode approved. Export is now available." : path.includes("revision") ? "Revision requested." : body.ready ? "Review is ready for approval." : "Review saved with blocking issues.");
      await load();
    } catch (e) { setError(e instanceof Error ? e.message : "Review action failed"); }
    finally { setBusy(false); }
  }

  return <AppShell title="Review Center">
    <section className="card">
      <div className="eyebrow">FINAL QUALITY GATE</div>
      <h2>Review Center</h2>
      <p className="muted">Video, audio, subtitle timing, thumbnail နဲ့ critical issues ကို final approval မတိုင်ခင် စစ်ဆေးပါ။</p>
      {error && <ErrorState message={error} retry={load} />}
      {message && <div className="success-state">{message}</div>}
    </section>
    <section className="card">
      <div className="eyebrow">APPROVAL CHECKLIST</div>
      {CHECKS.map(key => <label className="check-row" key={key}><input type="checkbox" checked={checks[key]} onChange={e => setChecks({ ...checks, [key]: e.target.checked })} /><span>{key.replaceAll("_", " ")}</span></label>)}
      <label>Critical issues<textarea rows={3} value={issues} onChange={e => setIssues(e.target.value)} placeholder="One issue per line. Leave empty when resolved." /></label>
      <label>Review notes<textarea rows={4} value={notes} onChange={e => setNotes(e.target.value)} /></label>
      <div className="inline-actions">
        <button className="text-button" disabled={busy} onClick={() => action("")}>Save review</button>
        <button className="text-button" disabled={busy} onClick={() => action("/request-revision")}>Request revision</button>
        <button className="primary" disabled={busy || review?.status !== "needs_approval"} onClick={() => action("/approve")}>Approve episode</button>
      </div>
    </section>
    {review?.blocking_reasons?.length ? <section className="card"><div className="eyebrow">BLOCKING ISSUES</div>{review.blocking_reasons.map((x: string, i: number) => <div className="list-card" key={i}><strong>BLOCKED</strong><span className="muted">{x}</span></div>)}</section> : null}
  </AppShell>;
}
