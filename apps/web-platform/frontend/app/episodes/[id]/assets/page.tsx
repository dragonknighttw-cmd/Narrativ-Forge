"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../../components/app-shell";
import { ErrorState } from "../../../../components/domain-forms";
import { api, Asset } from "../../../../lib/api";

export default function AssetLibraryPage() {
  const { id } = useParams<{ id: string }>();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [type, setType] = useState("video");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() { try { setError(""); setAssets(await api.listAssets(id)); } catch (e) { setError(e instanceof Error ? e.message : "Failed to load assets"); } }
  useEffect(() => { if (id) load(); }, [id]);

  async function upload() {
    if (!file) return; setBusy(true); setError("");
    try { await api.uploadAsset(id, file, type); setFile(null); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : "Upload failed"); } finally { setBusy(false); }
  }

  const [filter, setFilter] = useState("all");
  const [bgmTrackName, setBgmTrackName] = useState("");

  const filteredAssets = assets.filter(a => filter === "all" || a.asset_type === filter);

  return <AppShell title="Asset Library">
    <section className="card">
      <div className="eyebrow">9:16 SHORT-FORM PRODUCTION SPECIFICATION</div>
      <h2>Production Asset Requirements</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem", marginTop: "0.75rem" }}>
        <div style={{ padding: "0.75rem", borderRadius: "6px", background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.2)" }}>
          <strong style={{ color: "#6366f1" }}>📱 Aspect Ratio: 9:16 Vertical</strong>
          <p className="muted" style={{ fontSize: "0.85rem", margin: "0.25rem 0 0" }}>1080×1920 or 576×1024 portrait. Horizontal 16:9 will be cropped with pillarboxes.</p>
        </div>
        <div style={{ padding: "0.75rem", borderRadius: "6px", background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.2)" }}>
          <strong style={{ color: "#10b981" }}>🎵 Audio & BGM: 44.1/48kHz</strong>
          <p className="muted" style={{ fontSize: "0.85rem", margin: "0.25rem 0 0" }}>AAC-LC or PCM stereo. Normalization target: -14 to -16 LUFS with speech ducking.</p>
        </div>
        <div style={{ padding: "0.75rem", borderRadius: "6px", background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.2)" }}>
          <strong style={{ color: "#f59e0b" }}>🛡️ Commercial License Safety</strong>
          <p className="muted" style={{ fontSize: "0.85rem", margin: "0.25rem 0 0" }}>Verify copyright & watermarks before attaching assets to public distribution.</p>
        </div>
      </div>
    </section>

    <section className="card">
      <div className="eyebrow">UPLOAD</div>
      <h2>Add versioned production assets</h2>
      <p className="muted">Original uploads are stored separately and never overwritten by processing outputs.</p>
      {error && <ErrorState message={error} retry={load} />}
      <div className="inline-form" style={{ flexWrap: "wrap", gap: "0.75rem" }}>
        <select value={type} onChange={e => setType(e.target.value)} aria-label="Asset type" style={{ minWidth: "140px" }}>
          <option value="video">Video (9:16 MP4)</option>
          <option value="audio">Audio / BGM</option>
          <option value="image">Image (Background)</option>
          <option value="thumbnail">Thumbnail Cover</option>
        </select>
        <input
          type="file"
          accept={type === "video" ? "video/*" : type === "audio" ? "audio/*" : "image/*"}
          onChange={e => setFile(e.target.files?.[0] ?? null)}
        />
        <button className="primary" disabled={!file || busy} onClick={upload}>
          {busy ? "Uploading…" : "Upload Asset"}
        </button>
      </div>
    </section>

    <section className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
        <div className="eyebrow">ASSETS ({filteredAssets.length} / {assets.length})</div>
        <div style={{ display: "flex", gap: "0.35rem" }}>
          {["all", "video", "audio", "image", "thumbnail"].map(tab => (
            <button
              key={tab}
              className={filter === tab ? "primary" : "text-button"}
              style={{ padding: "0.25rem 0.6rem", fontSize: "0.8rem", textTransform: "capitalize" }}
              onClick={() => setFilter(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {filteredAssets.length === 0 ? (
        <div className="empty-state" style={{ marginTop: "1rem" }}>
          No {filter === "all" ? "" : filter} assets found. Upload media above to attach to this episode.
        </div>
      ) : (
        <div className="list" style={{ marginTop: "1rem" }}>
          {filteredAssets.map(asset => (
            <article className="list-card" key={asset.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <strong>v{asset.version} · {asset.original_filename}</strong>
                  <span className="pill" style={{ textTransform: "uppercase", fontSize: "0.7rem" }}>{asset.asset_type}</span>
                </div>
                <p className="muted" style={{ margin: "0.25rem 0 0", fontSize: "0.85rem" }}>
                  {asset.mime_type} · {Math.round(asset.file_size_bytes / 1024)} KB · Copyright: <span style={{ color: asset.copyright_status === "approved" ? "#10b981" : "#f59e0b" }}>{asset.copyright_status}</span>
                </p>
              </div>
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <span className="pill" style={{ background: asset.status === "ready" ? "rgba(16,185,129,0.15)" : "rgba(99,102,241,0.15)", color: asset.status === "ready" ? "#10b981" : "#6366f1" }}>
                  {asset.status}
                </span>
                <a
                  href={`/api/v1/assets/${asset.id}/download`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-button"
                  style={{ textDecoration: "none", fontSize: "0.85rem" }}
                >
                  Download
                </a>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  </AppShell>;
}
