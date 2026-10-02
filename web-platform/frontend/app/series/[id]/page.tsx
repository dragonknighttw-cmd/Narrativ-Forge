"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../components/app-shell";
import { ErrorState } from "../../../components/domain-forms";
import { api, Season, Series } from "../../../lib/api";

export default function SeriesDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [series, setSeries] = useState<Series | null>(null);
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [seasonNumber, setSeasonNumber] = useState("1");
  const [seasonTitle, setSeasonTitle] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    try { setError(""); const [s, ss] = await Promise.all([api.getSeries(id), api.listSeasons(id)]); setSeries(s); setSeasons(ss); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to load series"); }
  }
  useEffect(() => { if (id) load(); }, [id]);

  async function addSeason(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setError("");
    try { await api.createSeason(id, { season_number: Number(seasonNumber), title: seasonTitle.trim() || undefined }); setSeasonTitle(""); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to create season"); } finally { setBusy(false); }
  }

  if (error && !series) return <AppShell title="Series"><ErrorState message={error} retry={load} /></AppShell>;
  return <AppShell title={series?.title || "Series detail"}>
    {error && <ErrorState message={error} retry={load} />}
    <section className="card"><div className="eyebrow">SERIES</div><h2>{series?.title}</h2><p className="muted">{series?.description || "No description yet."}</p></section>
    <section className="card"><div className="eyebrow">SEASONS</div><h2>Season structure</h2>
      <form className="inline-form" onSubmit={addSeason}><input aria-label="Season number" type="number" min="1" value={seasonNumber} onChange={e => setSeasonNumber(e.target.value)} /><input aria-label="Season title" placeholder="Season title (optional)" value={seasonTitle} onChange={e => setSeasonTitle(e.target.value)} /><button className="primary" disabled={busy}>{busy ? "Saving…" : "Add season"}</button></form>
    </section>
    {!seasons.length && <section className="empty-state"><h3>No seasons yet</h3><p className="muted">Add season 1 to begin episode planning.</p></section>}
    <div className="list">{seasons.map(s => <article className="card list-item" key={s.id}><div><div className="eyebrow">SEASON {s.season_number}</div><h3>{s.title || "Untitled season"}</h3></div><span className="pill">{s.id.slice(0, 8)}</span></article>)}</div>
  </AppShell>;
}
