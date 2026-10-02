"use client";

import { useState } from "react";
import { AppShell } from "../../../components/app-shell";
import { ErrorState } from "../../../components/domain-forms";

export default function DriveExportPage({ params }: { params: { id: string } }) {
  const id = params.id;
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function exportNow() {
    setBusy(true); setError("");
    try {
      const response = await fetch("/api/v1/episodes/" + id + "/export/mock-drive", { method: "POST", credentials: "include" });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Drive export failed");
      setResult(body);
    } catch (e) { setError(e instanceof Error ? e.message : "Drive export failed"); }
    finally { setBusy(false); }
  }

  return <AppShell title="Drive Export">
    <section className="card">
      <div className="eyebrow">MOCK DRIVE</div>
      <h2>Export approved episode</h2>
      <p className="muted">Only an approved episode with a final video and approved subtitle can be exported. The export is idempotent and records a manifest.</p>
      {error && <ErrorState message={error} retry={exportNow} />}
      <button className="primary" disabled={busy} onClick={exportNow}>{busy ? "Exporting..." : "Export to Mock Drive"}</button>
    </section>
    {result && <section className="card"><div className="eyebrow">EXPORT MANIFEST</div><pre className="code-block">{JSON.stringify(result.manifest, null, 2)}</pre><p className="muted">Mock path: {result.mock_path ?? "already exported"}</p></section>}
  </AppShell>;
}
