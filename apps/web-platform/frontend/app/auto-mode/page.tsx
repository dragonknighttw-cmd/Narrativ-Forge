"use client";
import { FormEvent, useState } from "react";
import { AppShell } from "../../components/app-shell";
import { Alert, Button, Card, Stack, TextInput } from "../../components/ui-primitives";

const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(base + path, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!r.ok) {
    let detail = "Request failed";
    try {
      const body = await r.json();
      detail = typeof body.detail === "string" ? body.detail : body.detail?.message ?? detail;
    } catch {}
    throw new Error(detail);
  }
  return r.json();
}

export default function AutoModePage() {
  const [episodeId, setEpisodeId] = useState("");
  const [idea, setIdea] = useState("");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function run(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const data = await request<any>(
        "/auto/episodes/" + episodeId + "/run",
        { method: "POST", body: JSON.stringify({ idea }) },
      );
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Auto Mode failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell title="Auto Mode">
      <Stack>
        <div className="page-header">
          <div>
            <div className="eyebrow">AUTO PRODUCTION</div>
            <h2>Generate a production draft</h2>
            <p className="muted">Auto Mode prepares the draft pipeline; human review remains mandatory before export.</p>
          </div>
        </div>
        <Card>
          <form onSubmit={run} className="form-grid">
            <TextInput
              value={episodeId}
              onChange={e => setEpisodeId(e.target.value)}
              placeholder="Episode ID"
              aria-label="Episode ID"
              required
            />
            <TextInput
              value={idea}
              onChange={e => setIdea(e.target.value)}
              placeholder="Content idea"
              aria-label="Content idea"
              required
            />
            <Button type="submit" variant="primary" disabled={busy}>
              {busy ? "Starting…" : "Start Auto Mode"}
            </Button>
          </form>
          {error && <Alert tone="danger">{error}</Alert>}
          {result && (
            <Alert tone="success">
              <strong>Auto Mode started</strong>
              <p>Script: {result.script_id}</p>
              <p>Scenes: {result.scene_count}</p>
              <p>Processing job: {result.job_id}</p>
              <p>Pipeline: {result.next_steps.join(" → ")}</p>
              <p>Human review required: Yes</p>
            </Alert>
          )}
        </Card>
      </Stack>
    </AppShell>
  );
}
