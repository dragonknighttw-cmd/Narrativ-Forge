"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../../../components/app-shell";
import { ErrorState } from "../../../../../components/domain-forms";
import { api, Asset } from "../../../../../lib/api";

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

  return <AppShell title="Asset Library">
    <section className="card"><div className="eyebrow">UPLOAD</div><h2>Add versioned production assets</h2><p className="muted">Original uploads are stored separately and never overwritten by processing outputs.</p>{error && <ErrorState message={error} retry={load} />}
      <div className="inline-form"><select value={type} onChange={e => setType(e.target.value)} aria-label="Asset type"><option value="video">Video</option><option value="audio">Audio</option><option value="image">Image</option><option value="thumbnail">Thumbnail</option></select><input type="file" accept={type === "video" ? "video/*" : type === "audio" ? "audio/*" : "image/*"} onChange={e => setFile(e.target.files?.[0] ?? null)} /><button className="primary" disabled={!file || busy} onClick={upload}>{busy ? "Uploading…" : "Upload"}</button></div>
    </section>
    <section className="card"><div className="eyebrow">ASSETS</div>{assets.length === 0 ? <div className="empty-state">No assets uploaded yet.</div> : <div className="list">{assets.map(asset => <article className="list-card" key={asset.id}><div><strong>v{asset.version} · {asset.original_filename}</strong><p className="muted">{asset.asset_type} · {asset.mime_type} · {Math.round(asset.file_size_bytes / 1024)} KB · copyright: {asset.copyright_status}</p></div><span className="pill">{asset.status}</span></article>)}</div>}</section>
  </AppShell>;
}
