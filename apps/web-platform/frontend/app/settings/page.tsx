"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "../../../components/app-shell";
import { ErrorState } from "../../../components/domain-forms";
import { api } from "../../../lib/api";

type Account = Awaited<ReturnType<typeof api.me>>;
type Workspace = Awaited<ReturnType<typeof api.getWorkspace>>;
type ApiHealth = Awaited<ReturnType<typeof api.health>>;
type DriveStatus = Awaited<ReturnType<typeof api.getGoogleDriveStatus>>;

export default function SettingsPage() {
  const router = useRouter();
  const [account, setAccount] = useState<Account | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const [drive, setDrive] = useState<DriveStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    const results = await Promise.allSettled([
      api.me(), api.getWorkspace(), api.health(), api.getGoogleDriveStatus(),
    ]);
    if (results[0].status === "fulfilled") setAccount(results[0].value);
    if (results[1].status === "fulfilled") setWorkspace(results[1].value);
    if (results[2].status === "fulfilled") setHealth(results[2].value);
    if (results[3].status === "fulfilled") setDrive(results[3].value);
    const failed = results.find((result) => result.status === "rejected");
    if (failed?.status === "rejected") {
      setError(failed.reason instanceof Error ? failed.reason.message : "Some workspace settings could not be loaded");
    }
    setLoading(false);
  }

  useEffect(() => { void load(); }, []);

  async function connectDrive() {
    setBusy(true);
    setError("");
    try {
      const result = await api.getGoogleDriveStartUrl();
      window.location.assign(result.authorization_url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to start Google Drive connection");
      setBusy(false);
    }
  }

  async function signOut() {
    setBusy(true);
    setError("");
    try {
      await api.logout();
      router.replace("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign out");
      setBusy(false);
    }
  }

  return (
    <AppShell title="Settings">
      <div className="page-intro">
        <div className="eyebrow">WORKSPACE CONTROL</div>
        <h2>Account, workspace and connected services.</h2>
        <p className="muted">Sensitive credentials are never displayed here. Provider and integration states are reported separately from live workflow acceptance.</p>
      </div>
      {error && <ErrorState message={error} retry={load} />}

      <div className="settings-grid">
        <section className="card settings-card">
          <div className="eyebrow">SIGNED-IN ACCOUNT</div>
          <h3>Account details</h3>
          <div className="settings-detail"><span>Email</span><strong>{loading ? "Loading…" : account?.email ?? "Unavailable"}</strong></div>
          <div className="settings-detail"><span>Workspace role</span><strong>{loading ? "…" : account?.role ?? "Unavailable"}</strong></div>
          <div className="settings-detail"><span>Access model</span><strong>Invite-only</strong></div>
        </section>

        <section className="card settings-card">
          <div className="eyebrow">CURRENT WORKSPACE</div>
          <h3>Workspace profile</h3>
          <div className="settings-detail"><span>Name</span><strong>{loading ? "Loading…" : workspace?.name ?? "Unavailable"}</strong></div>
          <div className="settings-detail"><span>Workspace slug</span><strong>{loading ? "…" : workspace?.slug ?? "Unavailable"}</strong></div>
          <div className="settings-detail"><span>Plan</span><strong>{loading ? "…" : workspace?.plan ?? "Unavailable"}</strong></div>
        </section>

        <section className="card settings-card">
          <div className="eyebrow">CONNECTED SERVICES</div>
          <h3>Service status</h3>
          <div className="settings-integration-row">
            <div><strong>Application API</strong><span>{health?.service ?? "Health endpoint"}</span></div>
            <span className={health?.status === "ok" ? "ds-badge" : "ds-badge settings-status-muted"}>{loading ? "Checking" : health?.status ?? "Unavailable"}</span>
          </div>
          <div className="settings-integration-row">
            <div><strong>Google Drive</strong><span>{drive?.connected ? "Account connected" : "Not connected"}</span></div>
            <span className={drive?.connected ? "ds-badge" : "ds-badge settings-status-muted"}>{loading ? "Checking" : drive?.connected ? "Connected" : "Disconnected"}</span>
          </div>
          <button type="button" className="primary settings-action" onClick={connectDrive} disabled={loading || busy || Boolean(drive?.connected)}>
            {busy ? "Opening connection…" : drive?.connected ? "Google Drive connected" : "Connect Google Drive"}
          </button>
          <p className="settings-note">Drive connection uses Google OAuth. Final exports remain subject to the human approval gate.</p>
        </section>

        <section className="card settings-card">
          <div className="eyebrow">TELEGRAM WORKSPACE ROUTE</div>
          <h3>Review notifications</h3>
          <div className="settings-detail"><span>Project topic</span><strong>Narrativ Forge · Topic 6</strong></div>
          <p className="settings-note">This is the configured route. Live command, callback and approval tests are tracked separately; this page does not send messages or trigger approvals.</p>
        </section>

        <section className="card settings-card settings-session-card">
          <div className="eyebrow">SESSION SECURITY</div>
          <h3>End this session</h3>
          <p className="muted">Sign out of this browser session. You will need to sign in again to access the private workspace.</p>
          <button type="button" className="ds-button" onClick={signOut} disabled={busy || loading}>Sign out</button>
        </section>
      </div>
    </AppShell>
  );
}
