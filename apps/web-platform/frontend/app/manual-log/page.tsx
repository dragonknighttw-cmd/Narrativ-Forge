"use client";

import { FormEvent, useEffect, useState } from "react";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";
import { api, ManualProductionLog } from "../../lib/api";

export default function ManualProductionLogPage() {
  const [items, setItems] = useState<ManualProductionLog[]>([]);
  const [topic, setTopic] = useState("");
  const [production, setProduction] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setItems(await api.listProductionLogs());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load production logs");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, []);

  async function add(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!topic.trim()) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await api.createProductionLog({
        topic: topic.trim(),
        production_time_seconds: production.trim() ? Number(production) : null,
      });
      setTopic("");
      setProduction("");
      setSuccess("Production log saved.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save production log");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell title="Manual Production Log">
      <div className="page-intro">
        <div className="eyebrow">PRODUCTION INTELLIGENCE</div>
        <h2>Turn each production run into reusable knowledge.</h2>
        <p className="muted">မှတ်တမ်းတင်ထားတဲ့ production အချိန်နဲ့ topic တွေကို အနာဂတ် workflow တွေ ပိုကောင်းအောင် အသုံးချနိုင်ပါတယ်။</p>
      </div>

      <section className="card manual-log-form-card">
        <div className="eyebrow">NEW WORKFLOW ENTRY</div>
        <h3>Record a production session</h3>
        <form className="manual-log-form" onSubmit={add}>
          <label>
            <span>Topic / အကြောင်းအရာ</span>
            <input value={topic} onChange={(event) => setTopic(event.target.value)} maxLength={300} placeholder="ဥပမာ — ပုဂံခေတ် လျှို့ဝှက်ချက်များ" required />
          </label>
          <label>
            <span>Production time (seconds)</span>
            <input type="number" min="0" max="86400" value={production} onChange={(event) => setProduction(event.target.value)} placeholder="Optional" />
          </label>
          <button className="primary" type="submit" disabled={busy || !topic.trim()}>{busy ? "Saving…" : "Save production log"}</button>
        </form>
        {error && <ErrorState message={error} retry={load} />}
        {success && <p className="dashboard-inline-success" role="status">{success}</p>}
      </section>

      <section className="card">
        <div className="manual-log-list-heading">
          <div><div className="eyebrow">WORKSPACE HISTORY</div><h3>Production entries</h3></div>
          <span className="ds-badge">{loading ? "Loading" : `${items.length} entries`}</span>
        </div>
        {loading ? <div className="ds-empty" role="status">Loading production history…</div> :
          error && items.length === 0 ? null :
          items.length === 0 ? <div className="ds-empty"><strong>No production logs yet</strong><p>သင့်ရဲ့ ပထမဆုံး production session ကို မှတ်တမ်းတင်လိုက်ပါ။</p></div> :
          <div className="manual-log-list">
            {items.map((item) => (
              <article className="manual-log-item" key={item.id}>
                <div className="manual-log-item-mark" aria-hidden="true">NF</div>
                <div className="manual-log-item-copy">
                  <strong>{item.topic}</strong>
                  <span>{item.production_time_seconds == null ? "Time not recorded" : `${item.production_time_seconds.toLocaleString()} seconds`} · {new Date(item.created_at).toLocaleString()}</span>
                </div>
                <span className={item.published ? "ds-badge" : "ds-badge"}>{item.published ? "Published" : "Internal"}</span>
              </article>
            ))}
          </div>
        }
      </section>
    </AppShell>
  );
}
