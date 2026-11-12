"use client";
import Link from "next/link";
import { AppShell } from "../../components/app-shell";
import { api } from "../../lib/api";
import { useEffect, useState } from "react";

// ─── Brain Soul mini-status ───────────────────────────────────────
const BC = {
  lav: "#d8ff4f",
  green: "#7ec4a0",
  blue: "#80c9ff",
  border: "rgba(255,255,255,0.08)",
  dim: "#82919b",
};

function fmtD(iso: string | null) {
  if (!iso) return "—";
  const date = new Date(iso);
  return Number.isNaN(date.getTime())
    ? "—"
    : date.toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

interface BrainSoulStatus {
  tables_ready: boolean;
  total_syntheses: number;
  active_context_entries: number;
  latest_synthesis_at: string | null;
}

function BrainSoulMini() {
  const [data, setData] = useState<BrainSoulStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setData(await api.brainSoulStatus());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load Brain Soul status");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, []);

  async function synthesize() {
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const result = await api.brainSoulSynthesize();
      setMessage(result.reason || result.status || "Synthesis request completed.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Synthesis request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="brain-soul-panel" aria-labelledby="brain-soul-title">
      <div className="brain-soul-main">
        <div className="brain-soul-kicker">
          <span className="brain-soul-indicator" aria-hidden="true" />
          <span id="brain-soul-title">Brain Soul Layer</span>
          <span className="brain-soul-tag">MEMORY ENGINE</span>
        </div>
        <div className="brain-soul-stats">
          <div><span>Syntheses</span><strong>{loading ? "…" : data?.total_syntheses ?? "—"}</strong></div>
          <div><span>Soul Entries</span><strong>{loading ? "…" : data?.active_context_entries ?? "—"}</strong></div>
          <div><span>System</span><strong className="brain-soul-state">{loading ? "Checking" : data?.tables_ready ? "Ready" : data ? "Unavailable" : "Unknown"}</strong></div>
          <div><span>Last Synthesis</span><strong className="brain-soul-date">{fmtD(data?.latest_synthesis_at ?? null)}</strong></div>
        </div>
        {error && <p className="dashboard-inline-error" role="alert">{error}</p>}
        {message && <p className="dashboard-inline-success" role="status">{message}</p>}
      </div>
      <div className="brain-soul-actions">
        <Link href="/hooks" className="primary brain-soul-primary">SEO Hook Generator</Link>
        <button type="button" className="brain-soul-secondary" onClick={synthesize} disabled={busy || loading || !data?.tables_ready}>
          {busy ? "Working…" : "Synthesize Now"}
        </button>
      </div>
    </section>
  );
}

export default function DashboardPage() {
  const [episodeCount, setEpisodeCount] = useState<number | null>(null);
  const [episodesLoading, setEpisodesLoading] = useState(true);
  const [episodesError, setEpisodesError] = useState(false);
  const [usage, setUsage] = useState<Awaited<ReturnType<typeof api.aiUsage>> | null>(null);
  const [usageLoading, setUsageLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    api.listEpisodes()
      .then((episodes) => { if (mounted) setEpisodeCount(episodes.length); })
      .catch(() => { if (mounted) setEpisodesError(true); })
      .finally(() => { if (mounted) setEpisodesLoading(false); });
    api.aiUsage()
      .then((result) => { if (mounted) setUsage(result); })
      .catch(() => {})
      .finally(() => { if (mounted) setUsageLoading(false); });
    return () => { mounted = false; };
  }, []);

  const providers = usage?.providers ? Object.entries(usage.providers) : [];
  const activeProviders = providers.filter(([, provider]) => provider.status === "active").length;
  const chatChain = usage?.active_chains.chat_priority ?? [];
  const ragChain = usage?.active_chains.rag_priority ?? [];

  return (
    <AppShell title="Studio Overview">
      <section className="dashboard-hero">
        <div className="dashboard-hero-copy">
          <div className="dashboard-kicker"><span className="dashboard-kicker-line" /> PRODUCTION COMMAND CENTER</div>
          <h2>Your stories, from first spark to final cut.</h2>
          <p>
            A focused production workspace for Burmese short-form stories — plan ideas, shape scripts,
            build scenes, prepare subtitles, review every cut, and export approved masters.
          </p>
          <div className="dashboard-hero-actions">
            <Link href="/ideas" className="primary">Start with an idea <span aria-hidden="true">↗</span></Link>
            <Link href="/episodes" className="dashboard-secondary-link">View production queue</Link>
          </div>
        </div>
        <div className="dashboard-hero-art" aria-hidden="true">
          <div className="hero-art-orbit hero-art-orbit-one" />
          <div className="hero-art-orbit hero-art-orbit-two" />
          <div className="hero-art-core"><span>NF</span><small>STORY<br />ENGINE</small></div>
          <div className="hero-art-caption">IDEA → FRAME → STORY</div>
        </div>
      </section>

      <BrainSoulMini />

      <section className="dashboard-section" aria-labelledby="workspace-health-title">
        <div className="dashboard-section-heading">
          <div><div className="dashboard-kicker">WORKSPACE SNAPSHOT</div><h2 id="workspace-health-title">Production at a glance</h2></div>
          <span className="dashboard-updated-label">Live data where available</span>
        </div>
        <div className="dashboard-metrics">
          <article className="dashboard-metric-card">
            <span className="dashboard-metric-icon">▤</span>
            <span className="dashboard-metric-label">EPISODES</span>
            <strong>{episodesLoading ? "…" : episodesError ? "—" : (episodeCount ?? 0).toLocaleString()}</strong>
            <small>{episodesError ? "Could not load episode count" : "Records in your workspace"}</small>
          </article>
          <article className="dashboard-metric-card">
            <span className="dashboard-metric-icon">✳</span>
            <span className="dashboard-metric-label">AI PROVIDERS</span>
            <strong>{usageLoading ? "…" : usage ? `${activeProviders} / ${providers.length}` : "—"}</strong>
            <small>{usage ? "Provider status reported by API" : "Usage status unavailable"}</small>
          </article>
          <article className="dashboard-metric-card">
            <span className="dashboard-metric-icon">▧</span>
            <span className="dashboard-metric-label">SUBTITLE ROUTE</span>
            <strong className="dashboard-metric-word">Whisper</strong>
            <small>Cloudflare / Groq fallback path · verify on a real audio job</small>
          </article>
          <article className="dashboard-metric-card">
            <span className="dashboard-metric-icon">◎</span>
            <span className="dashboard-metric-label">TELEGRAM ROUTE</span>
            <strong className="dashboard-metric-word">Topic 6</strong>
            <small>Configured for Narrativ Forge · callback test pending</small>
          </article>
        </div>
      </section>

      <div className="dashboard-lower-grid">
        <section className="dashboard-panel" aria-labelledby="pipeline-title">
          <div className="dashboard-panel-heading">
            <div><div className="dashboard-kicker">THE CREATION FLOW</div><h2 id="pipeline-title">From concept to approved master</h2></div>
            <span className="dashboard-panel-count">04 STAGES</span>
          </div>
          <div className="pipeline-list">
            {[
              { number: "01", title: "Ideas & hook generation", desc: "Find the angle. Shape the opening.", href: "/ideas", action: "Explore ideas" },
              { number: "02", title: "Script & scene planning", desc: "Build a clear narrative with scene timing.", href: "/episodes", action: "Open episodes" },
              { number: "03", title: "Subtitles & media", desc: "Prepare Burmese captions and production assets.", href: "/subtitles", action: "Open subtitles" },
              { number: "04", title: "Review & approval", desc: "Keep human approval before final export.", href: "/review", action: "Review work" },
            ].map((stage) => (
              <div className="pipeline-item" key={stage.number}>
                <span className="pipeline-number">{stage.number}</span>
                <div className="pipeline-copy"><strong>{stage.title}</strong><span>{stage.desc}</span></div>
                <Link href={stage.href} className="pipeline-action" aria-label={stage.action}>{stage.action}<span aria-hidden="true">→</span></Link>
              </div>
            ))}
          </div>
        </section>

        <section className="dashboard-panel" aria-labelledby="resilience-title">
          <div className="dashboard-panel-heading">
            <div><div className="dashboard-kicker">AI ROUTING</div><h2 id="resilience-title">Provider priority</h2></div>
            <Link href="/usage" className="dashboard-panel-link">View health →</Link>
          </div>
          <div className="provider-chain-block">
            <div className="provider-chain-label">CHAT & SCRIPT</div>
            {chatChain.length ? chatChain.map((name, index) => (
              <div className="provider-chain-row" key={name}><span className="provider-chain-index">{index + 1}</span><span>{name}</span>{index === 0 ? <span className="provider-chain-first">PRIMARY</span> : null}</div>
            )) : <p className="provider-chain-empty">{usageLoading ? "Loading provider priority…" : "Provider priority is unavailable."}</p>}
          </div>
          <div className="provider-chain-block">
            <div className="provider-chain-label">KNOWLEDGE & EMBEDDINGS</div>
            {ragChain.length ? ragChain.map((name, index) => (
              <div className="provider-chain-row" key={name}><span className="provider-chain-index">{index + 1}</span><span>{name}</span>{index === 0 ? <span className="provider-chain-first">PRIMARY</span> : null}</div>
            )) : <p className="provider-chain-empty">{usageLoading ? "Loading embedding priority…" : "Embedding priority is unavailable."}</p>}
          </div>
          <p className="dashboard-disclaimer">Configured routing is not the same as a successful live inference. Check usage details and run a controlled test before production work.</p>
        </section>
      </div>
    </AppShell>
  );
}
