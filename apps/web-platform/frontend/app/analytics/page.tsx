"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";
import { api, AnalyticsSummary } from "../../lib/api";

const numberFormat = new Intl.NumberFormat("en-US");

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setData(await api.analyticsSummary());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, []);

  const metrics = data ? [
    { label: "Manual production logs", value: data.manual_logs, detail: `${data.published_logs} published` },
    { label: "Social analytics records", value: data.social_records, detail: "Recorded performance snapshots" },
    { label: "Total views", value: data.views, detail: "Across recorded analytics" },
    { label: "Watch time", value: data.watch_time_seconds, detail: "Seconds recorded" },
    { label: "Shares", value: data.shares, detail: "Recorded shares" },
    { label: "Saves", value: data.saves, detail: "Recorded saves" },
    { label: "Comments", value: data.comments, detail: "Recorded comments" },
    { label: "Average completion", value: Number(data.average_completion_rate.toFixed(2)), detail: "Reported average value" },
  ] : [];

  return (
    <AppShell title="App Analytics">
      <div className="page-intro analytics-intro">
        <div><div className="eyebrow">PRODUCTION + SOCIAL ANALYTICS</div><h2>Understand what is working.</h2><p className="muted">Production logs and manually recorded social performance, scoped to this workspace.</p></div>
        <button className="ds-button" type="button" onClick={() => void load()} disabled={loading}>{loading ? "Refreshing…" : "Refresh data"}</button>
      </div>

      {error && <ErrorState message={error} retry={load} />}

      <section className="analytics-metrics" aria-label="Analytics summary">
        {metrics.map((metric) => (
          <article className="analytics-metric" key={metric.label}>
            <span>{metric.label}</span>
            <strong>{loading ? "…" : numberFormat.format(metric.value)}</strong>
            <small>{metric.detail}</small>
          </article>
        ))}
      </section>

      {!loading && data && (
        <div className="analytics-breakdown-grid">
          <section className="card">
            <div className="eyebrow">CHANNEL PERFORMANCE</div>
            <h3>By platform</h3>
            {data.by_platform.length === 0 ? <div className="ds-empty">No social analytics recorded yet.</div> : (
              <div className="table-wrap"><table>
                <thead><tr><th>Platform</th><th>Records</th><th>Views</th><th>Shares</th><th>Saves</th></tr></thead>
                <tbody>{data.by_platform.map((row) => <tr key={row.platform}>
                  <td className="capitalize">{row.platform.replaceAll("_", " ")}</td>
                  <td>{numberFormat.format(row.records)}</td>
                  <td>{numberFormat.format(row.views)}</td>
                  <td>{numberFormat.format(row.shares)}</td>
                  <td>{numberFormat.format(row.saves)}</td>
                </tr>)}</tbody>
              </table></div>
            )}
          </section>

          <section className="card">
            <div className="eyebrow">CREATIVE PERFORMANCE</div>
            <h3>By hook type</h3>
            {data.by_hook_type.length === 0 ? <div className="ds-empty">No hook performance data recorded yet.</div> : (
              <div className="hook-analytics-list">{data.by_hook_type.map((row) => (
                <div className="hook-analytics-row" key={row.hook_type}>
                  <div><strong>{row.hook_type.replaceAll("_", " ")}</strong><span>{numberFormat.format(row.logs)} production logs</span></div>
                  <b>{numberFormat.format(row.views)} <small>views</small></b>
                </div>
              ))}</div>
            )}
          </section>
        </div>
      )}

      {loading && <div className="ds-empty" role="status">Loading workspace analytics…</div>}
      {!loading && data && data.manual_logs === 0 && data.social_records === 0 && <p className="analytics-footnote">Analytics will populate as production logs and social performance records are added. No synthetic or estimated metrics are shown.</p>}
    </AppShell>
  );
}
