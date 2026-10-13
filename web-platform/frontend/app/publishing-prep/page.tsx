"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";
import { api, Episode } from "../../lib/api";

const PLATFORMS = [
  { id: "tiktok", name: "TikTok", topMargin: "15%", bottomMargin: "22%", rightMargin: "18%" },
  { id: "youtube_shorts", name: "YouTube Shorts", topMargin: "12%", bottomMargin: "18%", rightMargin: "16%" },
  { id: "facebook_reels", name: "Facebook / IG Reels", topMargin: "10%", bottomMargin: "20%", rightMargin: "16%" },
];

export default function PublishingPreparationPage() {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [episodeId, setEpisodeId] = useState("");
  const [platform, setPlatform] = useState("tiktok");
  const [caption, setCaption] = useState("");
  const [hashtags, setHashtags] = useState("#မြန်မာ #ဗဟုသုတ #ဇာတ်လမ်းတွဲ #burmesestory #foryou");
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function loadEpisodes() {
    try {
      const e = await api.listEpisodes();
      setEpisodes(e);
      if (!episodeId && e[0]) setEpisodeId(e[0].id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load episodes");
    }
  }

  async function load() {
    if (!episodeId) return;
    try {
      const r = await fetch("/api/v1/episodes/" + episodeId + "/social-prep", { credentials: "include" });
      const b = await r.json();
      if (!r.ok) throw new Error(b.detail ?? "Failed to load publishing preparation");
      setItems(b);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load publishing preparation");
    }
  }

  useEffect(() => { loadEpisodes(); }, []);
  useEffect(() => { load(); }, [episodeId]);

  async function save() {
    setBusy(true);
    try {
      const r = await fetch("/api/v1/social-prep", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          episode_id: episodeId,
          platform,
          caption,
          hashtags: hashtags.split(/[ ,]+/).filter(Boolean),
          platform_format_valid: true,
        }),
      });
      const b = await r.json();
      if (!r.ok) throw new Error(b.detail ?? "Failed to save");
      setCaption("");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save");
    } finally {
      setBusy(false);
    }
  }

  const activePlatform = PLATFORMS.find(p => p.id === platform) || PLATFORMS[0];
  const selectedEpisode = episodes.find(e => e.id === episodeId);

  return (
    <AppShell title="Publishing Preparation">
      {/* 9:16 Cross-Platform Safe-Zone Simulator */}
      <section className="card">
        <div className="eyebrow">9:16 SAFE-ZONE VISUAL OVERLAY SIMULATOR</div>
        <h2>Verify Screen Clearance for {activePlatform.name}</h2>
        <p className="muted">Ensure hook titles and subtitles do not get obscured by platform UI buttons, icons, or captions.</p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.5rem", marginTop: "1rem" }}>
          {/* Mobile Screen Simulator */}
          <div style={{ display: "flex", justifyContent: "center" }}>
            <div style={{
              width: "240px",
              height: "426px",
              borderRadius: "16px",
              border: "3px solid #334155",
              background: "#090d16",
              position: "relative",
              overflow: "hidden",
              boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.5)",
            }}>
              {/* Top Obscured Area */}
              <div style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                height: activePlatform.topMargin,
                background: "rgba(239, 68, 68, 0.2)",
                borderBottom: "1px dashed #ef4444",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "10px",
                color: "#ef4444",
                fontWeight: 600,
              }}>
                Top Header Safe-Zone
              </div>

              {/* Right Side Engagement Column */}
              <div style={{
                position: "absolute",
                top: activePlatform.topMargin,
                bottom: activePlatform.bottomMargin,
                right: 0,
                width: activePlatform.rightMargin,
                background: "rgba(239, 68, 68, 0.2)",
                borderLeft: "1px dashed #ef4444",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "space-around",
                padding: "8px 0",
                fontSize: "9px",
                color: "#ef4444",
              }}>
                <span>❤️</span>
                <span>💬</span>
                <span>🔖</span>
                <span>↗️</span>
              </div>

              {/* Bottom Caption Area */}
              <div style={{
                position: "absolute",
                bottom: 0,
                left: 0,
                right: 0,
                height: activePlatform.bottomMargin,
                background: "rgba(239, 68, 68, 0.2)",
                borderTop: "1px dashed #ef4444",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "10px",
                color: "#ef4444",
                fontWeight: 600,
              }}>
                Caption & Sound Bar
              </div>

              {/* Center Safe Canvas */}
              <div style={{
                position: "absolute",
                top: activePlatform.topMargin,
                bottom: activePlatform.bottomMargin,
                left: "10px",
                right: activePlatform.rightMargin,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                padding: "8px",
              }}>
                <div style={{
                  padding: "8px",
                  borderRadius: "6px",
                  background: "rgba(16, 185, 129, 0.15)",
                  border: "1px solid #10b981",
                  color: "#10b981",
                  fontSize: "11px",
                  fontWeight: 600,
                }}>
                  ✅ 100% SAFE ZONE<br />
                  <span style={{ fontSize: "10px", color: "#f8fafc" }}>
                    {selectedEpisode?.title ? `"${selectedEpisode.title.slice(0, 25)}..."` : "Subtitles & Hooks appear here"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Guidelines */}
          <div className="stack-form">
            <div style={{ padding: "1rem", borderRadius: "8px", background: "rgba(99, 102, 241, 0.08)", border: "1px solid rgba(99, 102, 241, 0.2)" }}>
              <strong style={{ color: "#6366f1" }}>📱 {activePlatform.name} Safe-Zone Rules:</strong>
              <ul style={{ margin: "0.5rem 0 0 1rem", fontSize: "0.85rem", lineHeight: 1.6 }} className="muted">
                <li>Keep titles below top {activePlatform.topMargin} to avoid status bars.</li>
                <li>Keep main Burmese text away from the right {activePlatform.rightMargin} to prevent overlap with engagement icons.</li>
                <li>Position subtitles at least {activePlatform.bottomMargin} above the bottom edge.</li>
                <li>Recommended Burmese posting window: <strong>7:00 PM – 9:30 PM MMT</strong>.</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Manual Publishing Preparation Form */}
      <section className="card">
        <div className="eyebrow">METADATA PREPARATION</div>
        <h2>Prepare Captions & SEO Tags</h2>
        <p className="muted">Draft platform-tailored metadata for manual distribution. Actual posting remains manual.</p>
        {error && <ErrorState message={error} retry={load} />}

        <div className="stack-form">
          <div className="inline-form" style={{ flexWrap: "wrap", gap: "0.75rem" }}>
            <select value={episodeId} onChange={e => setEpisodeId(e.target.value)} style={{ minWidth: "220px" }}>
              {episodes.map(e => <option value={e.id} key={e.id}>{e.public_id} · {e.title}</option>)}
            </select>
            <select value={platform} onChange={e => setPlatform(e.target.value)} style={{ minWidth: "180px" }}>
              {PLATFORMS.map(p => <option value={p.id} key={p.id}>{p.name}</option>)}
            </select>
          </div>

          <label>
            Caption (မြန်မာဘာသာဖြင့် ဖော်ပြချက်)
            <textarea
              className="burmese-text"
              value={caption}
              onChange={e => setCaption(e.target.value)}
              placeholder="ဇာတ်လမ်းတွဲ အကြောင်းအရာကို ဆွဲဆောင်မှုရှိစွာ ရေးသားပါ…"
              rows={4}
            />
          </label>

          <label>
            Hashtags (SEO Tag များ)
            <input
              value={hashtags}
              onChange={e => setHashtags(e.target.value)}
              placeholder="#burmese #story #knowledge"
            />
          </label>

          <div>
            <button className="primary" disabled={!episodeId || busy} onClick={save}>
              {busy ? "Saving…" : "Save Publishing Metadata"}
            </button>
          </div>
        </div>
      </section>

      {/* Preparation History */}
      <section className="card">
        <div className="eyebrow">SAVED PREPARATIONS ({items.length})</div>
        {items.length === 0 ? (
          <div className="empty-state" style={{ marginTop: "1rem" }}>
            No publishing preparation saved yet.
          </div>
        ) : (
          <div className="list" style={{ marginTop: "1rem" }}>
            {items.map(x => (
              <div className="list-card" key={x.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                    <strong>{x.platform.toUpperCase()}</strong>
                    <span className="pill" style={{ fontSize: "0.75rem" }}>{x.state}</span>
                  </div>
                  <p className="burmese-text muted" style={{ margin: "0.25rem 0 0", fontSize: "0.85rem" }}>
                    {x.caption || "No caption"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </AppShell>
  );
}