"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";
import { api, Episode, Series } from "../../lib/api";

export default function EpisodesPage() {
  const [items, setItems] = useState<Episode[]>([]);
  const [series, setSeries] = useState<Series[]>([]);
  const [seriesId, setSeriesId] = useState("");
  const [episodeNumber, setEpisodeNumber] = useState("1");
  const [title, setTitle] = useState("");
  const [duration, setDuration] = useState("180");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function load() { try { setError(""); const [e, s] = await Promise.all([api.listEpisodes(), api.listSeries()]); setItems(e); setSeries(s); if (!seriesId && s[0]) setSeriesId(s[0].id); } catch (e) { setError(e instanceof Error ? e.message : "Failed to load episodes"); } }
  useEffect(() => { load(); }, []);
  const seriesName = useMemo(() => Object.fromEntries(series.map(s => [s.id, s.title])), [series]);

  async function add(e: React.FormEvent) {
    e.preventDefault(); if (!seriesId || !title.trim()) return;
    setBusy(true); setError("");
    try { await api.createEpisode({ series_id: seriesId, episode_number: Number(episodeNumber), title: title.trim(), target_duration_seconds: Number(duration) }); setTitle(""); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to create episode"); } finally { setBusy(false); }
  }

  // 5-Episode Batch Generator state
  const [batchTheme, setBatchTheme] = useState("");
  const [batchCategory, setBatchCategory] = useState("general");
  const [batchDuration, setBatchDuration] = useState("180");
  const [batchBusy, setBatchBusy] = useState(false);
  const [batchMessage, setBatchMessage] = useState("");
  const [batchPreview, setBatchPreview] = useState<any[] | null>(null);

  async function generateBatch(commit: boolean) {
    if (!batchTheme.trim()) return;
    setBatchBusy(true); setBatchMessage(""); setError("");
    try {
      const res = await api.batchGenerateEpisodes({
        theme: batchTheme.trim(),
        category: batchCategory,
        series_id: seriesId || undefined,
        target_duration_seconds: Number(batchDuration),
        commit,
      });
      if (!commit && res.plan) {
        setBatchPreview(res.plan.episodes);
        setBatchMessage("5-Episode Batch preview generated. Review the arc below and click Commit to create all 5 episodes.");
      } else if (commit) {
        setBatchMessage(res.message);
        setBatchPreview(null);
        setBatchTheme("");
        await load();
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Batch generation failed");
    } finally {
      setBatchBusy(false);
    }
  }

  return <AppShell title="Episodes">
    <section className="card">
      <div className="eyebrow">5-EPISODE BATCH GENERATOR · AUTOMATED MINI-SERIES ARC</div>
      <h2>AI 5-Episode Batch Generator</h2>
      <p className="muted">အကြောင်းအရာ တစ်ခုတည်းမှ အပိုင်း ၅ ပိုင်းပါဝင်သော စီးရီးဇာတ်လမ်း arc (Mystery → Shock → Warning → Contrarian → Payoff) ကို တစ်ခါတည်း ထုတ်လုပ်ပေးပါသည်။</p>
      {batchMessage && <div className="success" style={{ marginTop: "12px" }}>{batchMessage}</div>}
      <div className="stack-form" style={{ marginTop: "14px" }}>
        <input
          required
          maxLength={300}
          placeholder="မိတ်ဆက်လိုသော အဓိက အကြောင်းအရာ/ခေါင်းစဉ် (ဥပမာ - ပုဂံခေတ် လျှို့ဝှက်ချက်များ)"
          value={batchTheme}
          onChange={e => setBatchTheme(e.target.value)}
          className="burmese-text"
        />
        <div className="form-row">
          <select value={batchCategory} onChange={e => setBatchCategory(e.target.value)} aria-label="Category">
            <option value="general">အထွေထွေ (General)</option>
            <option value="history">သမိုင်းနှင့် ရှေးဟောင်း (History)</option>
            <option value="mystery">လျှို့ဝှက်ဆန်းကြယ် (Mystery)</option>
            <option value="tech">နည်းပညာ (Tech)</option>
            <option value="lifestyle">လူနေမှုဘဝ (Lifestyle)</option>
          </select>
          <input
            type="number"
            min="60"
            max="300"
            value={batchDuration}
            onChange={e => setBatchDuration(e.target.value)}
            aria-label="Target duration per episode"
          />
          <div className="ds-row">
            <button
              type="button"
              className="text-button"
              disabled={batchBusy || !batchTheme.trim()}
              onClick={() => generateBatch(false)}
            >
              {batchBusy ? "Generating…" : "Preview Arc"}
            </button>
            <button
              type="button"
              className="primary"
              disabled={batchBusy || !batchTheme.trim()}
              onClick={() => generateBatch(true)}
            >
              Commit & Create 5 Episodes
            </button>
          </div>
        </div>
      </div>

      {batchPreview && (
        <div style={{ marginTop: "20px", display: "grid", gap: "12px" }}>
          <div className="eyebrow">PREVIEW OF 5-EPISODE NARRATIVE ARC</div>
          {batchPreview.map((ep: any) => (
            <div className="card" key={ep.episode_number} style={{ background: "var(--surface2)", border: "1px solid var(--border)", padding: "14px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <strong>{ep.title}</strong>
                <span className="pill">{ep.hook_family}</span>
              </div>
              <p style={{ fontSize: "13px", color: "var(--accent)", margin: "6px 0" }}>Hook: {ep.hook}</p>
              <p className="muted" style={{ fontSize: "12px", margin: "4px 0" }}>{ep.synopsis}</p>
              <small style={{ color: "var(--color-warning)" }}>Cliffhanger: {ep.cliffhanger}</small>
            </div>
          ))}
          <button
            type="button"
            className="primary"
            style={{ marginTop: "10px" }}
            disabled={batchBusy}
            onClick={() => generateBatch(true)}
          >
            Confirm & Commit All 5 Episodes
          </button>
        </div>
      )}
    </section>

    <section className="card"><div className="eyebrow">STAGE 2 · STRUCTURE</div><h2>Single Episode Planning</h2><p className="muted">Every episode belongs to a series. Season linkage can be added when the season structure exists.</p>
      {!series.length ? <div className="empty-state"><h3>Create a series first</h3><p className="muted">Episodes require a valid series relationship.</p><Link className="text-button" href="/series">Go to Series →</Link></div> :
      <form className="stack-form" onSubmit={add}><select value={seriesId} onChange={e => setSeriesId(e.target.value)} aria-label="Series">{series.map(s => <option key={s.id} value={s.id}>{s.title}</option>)}</select><div className="form-row"><input aria-label="Episode number" type="number" min="1" value={episodeNumber} onChange={e => setEpisodeNumber(e.target.value)} /><input aria-label="Target duration" type="number" min="1" value={duration} onChange={e => setDuration(e.target.value)} /><input required maxLength={255} placeholder="Episode title" value={title} onChange={e => setTitle(e.target.value)} /></div><button className="primary" disabled={busy}>{busy ? "Saving…" : "Create episode"}</button></form>}
    </section>
    {error && <ErrorState message={error} retry={load} />}
    {!error && !items.length && <section className="empty-state"><h3>No episodes yet</h3><p className="muted">Episodes will appear here after creation.</p></section>}
    <div className="list">{items.map(item => <Link href={"/episodes/" + item.id} className="card list-item" key={item.id}><div><div className="eyebrow">{seriesName[item.series_id] || "Series"} · E{item.episode_number}</div><h3>{item.title}</h3><p className="muted">{item.public_id} · Target {item.target_duration_seconds}s</p></div><span className="pill">{item.status}</span></Link>)}</div>

  </AppShell>;
}
