"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../../components/app-shell";
import { ErrorState } from "../../../components/domain-forms";

export default function DriveExportPage({ params }: { params: { id: string } }) {
  const id = params.id;
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [connected, setConnected] = useState(false);

  async function checkDrive() {
    const r = await fetch("/api/v1/drive/google/status", { credentials: "include" });
    if (r.ok) setConnected((await r.json()).connected);
  }

  async function connectDrive() {
    const r = await fetch("/api/v1/drive/google/start", { credentials: "include" });
    const body = await r.json();
    if (!r.ok) throw new Error(body.detail ?? "Drive connection failed");
    window.location.href = body.authorization_url;
  }

  async function exportNow(provider: "mock-drive" | "google-drive") {
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/v1/episodes/" + id + "/export/" + provider, { method: "POST", credentials: "include" });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Drive export failed");
      setResult(body);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Drive export failed");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => { checkDrive().catch(() => setConnected(false)); }, []);

  return <AppShell title="Drive Export">
    <section className="card">
      <div className="eyebrow">DRIVE EXPORT</div>
      <h2>Export approved episode</h2>
      <p className="muted">Only an approved episode with a final video and approved subtitle can be exported. Completed exports are idempotent.</p>
      {error && <ErrorState message={error} retry={() => exportNow("mock-drive")} />}
      <div className="inline-actions">
        <button className="text-button" onClick={() => connectDrive().catch(e => setError(e.message))}>
          {connected ? "Google Drive connected" : "Connect Google Drive"}
        </button>
        <button className="text-button" disabled={busy || !connected} onClick={() => exportNow("google-drive")}>Export to Google Drive</button>
        <button className="primary" disabled={busy} onClick={() => exportNow("mock-drive")}>Export to Mock Drive</button>
      </div>
    </section>
    {result && <section className="card">
      <div className="eyebrow">EXPORT MANIFEST</div>
      <pre className="code-block">{JSON.stringify(result.manifest, null, 2)}</pre>
      <p className="muted">Mock path: {result.mock_path ?? "—"}</p>
    </section>}
  </AppShell>;
}
