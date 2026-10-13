"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../../components/app-shell";
import { ErrorState } from "../../../../components/domain-forms";

const CHECKS = ["video_watched", "audio_checked", "subtitle_timing_checked", "thumbnail_present"] as const;

export default function ReviewCenterPage() {
  const { id } = useParams<{ id: string }>();
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
  const [thumbnailData, setThumbnailData] = useState<{
    total_generated: number;
    candidates: any[];
    shortlisted: any[];
    approved?: any;
  } | null>(null);
  const [thumbBusy, setThumbBusy] = useState(false);

  async function loadThumbnails() {
    try {
      setThumbBusy(true);
      const res = await fetch("/api/v1/episodes/" + id + "/review/thumbnails", { credentials: "include" });
      if (res.ok) {
        const body = await res.json();
        setThumbnailData(body);
      }
    } catch {
      // safe fallback
    } finally {
      setThumbBusy(false);
    }
  }

  async function approveThumb(c: any) {
    try {
      setThumbBusy(true);
      const res = await fetch("/api/v1/episodes/" + id + "/review/thumbnails/approve", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_id: c.id,
          visual_prompt: c.visual_prompt,
          overlay_text: c.overlay_text,
          notes: "Approved from Review Center",
        }),
      });
      if (res.ok) {
        setMessage(`Thumbnail candidate '${c.id}' approved.`);
        await load();
        await loadThumbnails();
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to approve thumbnail");
    } finally {
      setThumbBusy(false);
    }
  }

  useEffect(() => { load(); loadThumbnails(); }, [id]);

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
      {message && <div className="success">{message}</div>}
    </section>

    <section className="card">
      <div className="eyebrow">THUMBNAIL CANDIDATE SELECTION (10 GENERATED → 5 SHORTLISTED → 1 APPROVED)</div>
      <h2>Thumbnail Candidates</h2>
      <p className="muted">AI မှ short-form ဗီဒီယိုအတွက် အကောင်းဆုံး Thumbnail စိတ်ကူး ၁၀ ခုကို ထုတ်လုပ်ပြီး အမြင့်ဆုံး Click-Through-Rate ရနိုင်မယ့် ထိပ်တန်း ၅ ခုကို ရွေးချယ်ပေးထားပါတယ်။</p>

      {thumbnailData?.approved ? (
        <div className="success" style={{ marginTop: "12px" }}>
          <strong>✓ Thumbnail Approved</strong>
          <p className="muted">Thumbnail ရွေးချယ်အတည်ပြုပြီးပါပြီ။ Checklist တွင် အလိုအလျောက် မှတ်သားထားပါသည်။</p>
        </div>
      ) : null}

      <div className="inline-actions" style={{ margin: "14px 0" }}>
        <button
          className="text-button"
          disabled={thumbBusy}
          onClick={loadThumbnails}
        >
          {thumbBusy ? "Generating…" : "↻ Refresh / Generate Candidates"}
        </button>
      </div>

      {thumbnailData?.shortlisted?.length ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "14px", marginTop: "14px" }}>
          {thumbnailData.shortlisted.map((c: any) => (
            <div className="card" key={c.id} style={{ border: "1px solid var(--border)", background: "var(--surface2)", padding: "14px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <span className="pill">{c.composition_style}</span>
                  <span style={{ fontSize: "12px", color: "var(--accent)", fontWeight: 700 }}>Score: {c.score}</span>
                </div>
                <div style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "8px", padding: "12px", textAlign: "center", marginBottom: "10px" }}>
                  <span style={{ fontSize: "16px", fontWeight: 800, color: "var(--accent)" }}>{c.overlay_text}</span>
                </div>
                <p style={{ fontSize: "12px", color: "var(--text)", lineHeight: 1.5, marginBottom: "8px" }}>{c.visual_prompt}</p>
                <small className="muted" style={{ display: "block", marginBottom: "12px" }}>{c.reason}</small>
              </div>
              <button
                className="primary"
                style={{ width: "100%", fontSize: "13px", padding: "8px" }}
                disabled={thumbBusy}
                onClick={() => approveThumb(c)}
              >
                Approve this Thumbnail
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">No candidates loaded yet. Click the button above to generate 10 candidates and shortlist the top 5.</div>
      )}
    </section>

    <section className="card">
      <div className="eyebrow">APPROVAL CHECKLIST</div>
      {CHECKS.map(key => <label className="check-row" key={key} style={{ display: "flex", gap: "8px", alignItems: "center", margin: "8px 0" }}><input type="checkbox" checked={checks[key]} onChange={e => setChecks({ ...checks, [key]: e.target.checked })} /><span>{key.replaceAll("_", " ")}</span></label>)}
      <label style={{ display: "block", marginTop: "12px" }}>Critical issues<textarea rows={3} value={issues} onChange={e => setIssues(e.target.value)} placeholder="One issue per line. Leave empty when resolved." style={{ width: "100%", marginTop: "6px" }} /></label>
      <label style={{ display: "block", marginTop: "12px" }}>Review notes<textarea rows={4} value={notes} onChange={e => setNotes(e.target.value)} style={{ width: "100%", marginTop: "6px" }} /></label>
      <div className="inline-actions" style={{ marginTop: "16px" }}>
        <button className="text-button" disabled={busy} onClick={() => action("")}>Save review</button>
        <button className="text-button" disabled={busy} onClick={() => action("/request-revision")}>Request revision</button>
        <button className="primary" disabled={busy || review?.status !== "needs_approval"} onClick={() => action("/approve")}>Approve episode</button>
      </div>
    </section>
    {review?.blocking_reasons?.length ? <section className="card"><div className="eyebrow">BLOCKING ISSUES</div>{review.blocking_reasons.map((x: string, i: number) => <div className="list-card" key={i}><strong>BLOCKED</strong><span className="muted">{x}</span></div>)}</section> : null}
  </AppShell>;
}
