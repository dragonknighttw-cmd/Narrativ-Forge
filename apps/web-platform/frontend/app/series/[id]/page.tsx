"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../components/app-shell";
import { ErrorState } from "../../../components/domain-forms";
import { api, Season, Series, SeriesBibleCharacter } from "../../../lib/api";

export default function SeriesDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [series, setSeries] = useState<Series | null>(null);
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [seasonNumber, setSeasonNumber] = useState("1");
  const [seasonTitle, setSeasonTitle] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editing, setEditing] = useState(false);

  async function load() {
    try { setError(""); const [s, ss] = await Promise.all([api.getSeries(id), api.listSeasons(id)]); setSeries(s); setSeasons(ss); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to load series"); }
  }
  useEffect(() => { if (id) load(); }, [id]);
  useEffect(() => { if (series) { setEditTitle(series.title); setEditDescription(series.description || ""); } }, [series]);

  async function addSeason(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setError("");
    try { await api.createSeason(id, { season_number: Number(seasonNumber), title: seasonTitle.trim() || undefined }); setSeasonTitle(""); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to create season"); } finally { setBusy(false); }
  }

  // Series Bible & Character Continuity State
  const [characters, setCharacters] = useState<SeriesBibleCharacter[]>([]);
  const [bibleBusy, setBibleBusy] = useState(false);
  const [bibleLoaded, setBibleLoaded] = useState(false);
  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    api.getSeriesBible(id)
      .then(result => {
        if (!cancelled) setCharacters(result.characters);
      })
      .catch(e => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load Series Bible");
      })
      .finally(() => {
        if (!cancelled) setBibleLoaded(true);
      });
    return () => { cancelled = true; };
  }, [id]);
  const [newCharName, setNewCharName] = useState("");
  const [newCharRole, setNewCharRole] = useState<"protagonist" | "antagonist" | "mentor" | "sidekick">("protagonist");
  const [newCharTone, setNewCharTone] = useState("");
  const [newCharCatchphrase, setNewCharCatchphrase] = useState("");
  const [newCharTraits, setNewCharTraits] = useState("");

  async function addCharacter(e: React.FormEvent) {
    e.preventDefault();
    if (!newCharName.trim() || bibleBusy) return;
    const item: SeriesBibleCharacter = {
      id: crypto.randomUUID(),
      name: newCharName.trim(),
      role: newCharRole,
      tone: newCharTone.trim() || "Natural Burmese conversational tone",
      catchphrase: newCharCatchphrase.trim(),
      traits: newCharTraits.trim(),
    };
    setBibleBusy(true);
    setError("");
    try {
      const saved = await api.updateSeriesBible(id, [...characters, item]);
      setCharacters(saved.characters);
      setNewCharName("");
      setNewCharTone("");
      setNewCharCatchphrase("");
      setNewCharTraits("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save Series Bible character");
    } finally {
      setBibleBusy(false);
    }
  }

  async function removeCharacter(charId: string) {
    if (bibleBusy) return;
    setBibleBusy(true);
    setError("");
    try {
      const saved = await api.updateSeriesBible(id, characters.filter(c => c.id !== charId));
      setCharacters(saved.characters);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to remove Series Bible character");
    } finally {
      setBibleBusy(false);
    }
  }

  if (error && !series) return <AppShell title="Series"><ErrorState message={error} retry={load} /></AppShell>;
  return <AppShell title={series?.title || "Series detail"}>
    {error && <ErrorState message={error} retry={load} />}
    <section className="card"><div className="eyebrow">SERIES</div>{editing ? <div className="stack-form"><input value={editTitle} onChange={e => setEditTitle(e.target.value)} /><textarea value={editDescription} onChange={e => setEditDescription(e.target.value)} /><div className="inline-form"><button className="primary" disabled={busy} onClick={async () => { setBusy(true); try { await api.updateSeries(id, { title: editTitle.trim(), description: editDescription.trim() || null }); setEditing(false); await load(); } catch (e) { setError(e instanceof Error ? e.message : "Failed to update series"); } finally { setBusy(false); } }}>Save</button><button className="text-button" onClick={() => setEditing(false)}>Cancel</button></div></div> : <><h2>{series?.title}</h2><p className="muted">{series?.description || "No description yet."}</p><button className="text-button" onClick={() => setEditing(true)}>Edit series</button></>}</section>

    {/* Series Bible & Character Consistency */}
    <section className="card">
      <div className="eyebrow">SERIES BIBLE & CHARACTER CONTINUITY</div>
      <h2>Character Voice & Style Bible</h2>
      <p className="muted">Maintain consistent character voices, archetypes, and narrative rules across all episodes in this series.</p>

      {/* Characters List */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem", marginTop: "1rem" }}>
        {characters.map(char => (
          <article key={char.id} className="list-card" style={{ display: "block", padding: "1rem", background: "#0f172a", border: "1px solid #334155" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <strong>{char.name}</strong>
                <span className="pill" style={{ marginLeft: "0.5rem", textTransform: "capitalize", fontSize: "0.75rem" }}>{char.role}</span>
              </div>
              <button className="text-button" style={{ color: "#ef4444", padding: 0 }} disabled={bibleBusy} onClick={() => void removeCharacter(char.id)}>✕</button>
            </div>
            <p className="muted burmese-text" style={{ fontSize: "0.85rem", marginTop: "0.5rem", marginBottom: "0.25rem" }}>
              🎙️ <strong>Tone:</strong> {char.tone}
            </p>
            {char.catchphrase && (
              <p className="burmese-text" style={{ fontSize: "0.85rem", color: "#6366f1", margin: "0.25rem 0" }}>
                💬 <em>"{char.catchphrase}"</em>
              </p>
            )}
            {char.traits && (
              <p className="muted burmese-text" style={{ fontSize: "0.8rem", margin: "0.25rem 0 0" }}>
                📝 {char.traits}
              </p>
            )}
          </article>
        ))}
      </div>

      {/* Add Character Form */}
      <form onSubmit={addCharacter} className="stack-form" style={{ marginTop: "1.5rem", padding: "1rem", borderRadius: "8px", background: "rgba(99, 102, 241, 0.05)", border: "1px dashed rgba(99, 102, 241, 0.3)" }}>
        <strong style={{ fontSize: "0.9rem" }}>+ Add Series Character</strong>
        {!bibleLoaded && <p className="muted">Loading saved Series Bible…</p>}
        {bibleLoaded && characters.length === 0 && <p className="muted">No saved characters yet. Add one below.</p>}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.75rem" }}>
          <input
            placeholder="Character name (e.g. ဇေယျာ)"
            value={newCharName}
            onChange={e => setNewCharName(e.target.value)}
            required
          />
          <select
            value={newCharRole}
            onChange={e => setNewCharRole(e.target.value as any)}
          >
            <option value="protagonist">Protagonist (အဓိကဇာတ်ကောင်)</option>
            <option value="antagonist">Antagonist (ပြိုင်ဘက်/ဗီလိန်)</option>
            <option value="mentor">Mentor (လမ်းညွှန်ဆရာ)</option>
            <option value="sidekick">Sidekick (အကူဇာတ်ကောင်)</option>
          </select>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.75rem" }}>
          <input
            placeholder="Voice tone (e.g. Serious, playful, confident)"
            value={newCharTone}
            onChange={e => setNewCharTone(e.target.value)}
          />
          <input
            placeholder="Catchphrase (မြန်မာစကားထာ/အသုံးအနှုန်း)"
            value={newCharCatchphrase}
            onChange={e => setNewCharCatchphrase(e.target.value)}
          />
        </div>
        <input
          placeholder="Visual description / traits (ရုပ်သွင်ပြင်လက္ခဏာ)"
          value={newCharTraits}
          onChange={e => setNewCharTraits(e.target.value)}
        />
        <div>
          <button type="submit" className="primary" disabled={!newCharName.trim() || bibleBusy || !bibleLoaded}>{bibleBusy ? "Saving…" : "Save Character"}</button>
        </div>
      </form>
    </section>

    <section className="card"><div className="eyebrow">SEASONS</div><h2>Season structure</h2>
      <form className="inline-form" onSubmit={addSeason}><input aria-label="Season number" type="number" min="1" value={seasonNumber} onChange={e => setSeasonNumber(e.target.value)} /><input aria-label="Season title" placeholder="Season title (optional)" value={seasonTitle} onChange={e => setSeasonTitle(e.target.value)} /><button className="primary" disabled={busy}>{busy ? "Saving…" : "Add season"}</button></form>
    </section>
    {!seasons.length && <section className="empty-state"><h3>No seasons yet</h3><p className="muted">Add season 1 to begin episode planning.</p></section>}
    <div className="list">{seasons.map(s => <article className="card list-item" key={s.id}><div><div className="eyebrow">SEASON {s.season_number}</div><h3>{s.title || "Untitled season"}</h3></div><span className="pill">{s.id.slice(0, 8)}</span></article>)}</div>
  </AppShell>;
}
