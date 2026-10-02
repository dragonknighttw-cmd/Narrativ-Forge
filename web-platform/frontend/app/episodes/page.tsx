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

  return <AppShell title="Episodes">
    <section className="card"><div className="eyebrow">STAGE 2 · STRUCTURE</div><h2>Episode planning</h2><p className="muted">Every episode belongs to a series. Season linkage can be added when the season structure exists.</p>
      {!series.length ? <div className="empty-state"><h3>Create a series first</h3><p className="muted">Episodes require a valid series relationship.</p><Link className="text-button" href="/series">Go to Series →</Link></div> :
      <form className="stack-form" onSubmit={add}><select value={seriesId} onChange={e => setSeriesId(e.target.value)} aria-label="Series">{series.map(s => <option key={s.id} value={s.id}>{s.title}</option>)}</select><div className="form-row"><input aria-label="Episode number" type="number" min="1" value={episodeNumber} onChange={e => setEpisodeNumber(e.target.value)} /><input aria-label="Target duration" type="number" min="1" value={duration} onChange={e => setDuration(e.target.value)} /><input required maxLength={255} placeholder="Episode title" value={title} onChange={e => setTitle(e.target.value)} /></div><button className="primary" disabled={busy}>{busy ? "Saving…" : "Create episode"}</button></form>}
    </section>
    {error && <ErrorState message={error} retry={load} />}
    {!error && !items.length && <section className="empty-state"><h3>No episodes yet</h3><p className="muted">Episodes will appear here after creation.</p></section>}
    <div className="list">{items.map(item => <Link href={"/episodes/" + item.id} className="card list-item" key={item.id}><div><div className="eyebrow">{seriesName[item.series_id] || "Series"} · E{item.episode_number}</div><h3>{item.title}</h3><p className="muted">{item.public_id} · Target {item.target_duration_seconds}s</p></div><span className="pill">{item.status}</span></Link>)}</div>
  </AppShell>;
}
