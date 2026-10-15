"use client";
import { useEffect, useState } from "react";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";

// ─── Types ───────────────────────────────────────────────────────
interface HookItem {
  id: number;
  hook_text: string;
  hook_type: string;
  used_count: number;
  performance_score: number | null;
  is_default: boolean;
  topic: string | null;
}

interface SeoHookVariant {
  style: string;
  hook_text: string;
  score: number;
  reasoning: string;
}

interface SeoResponse {
  story_title: string;
  hooks: SeoHookVariant[];
  best_hook: string;
  seo_keywords: string[];
}

// ─── Pastel colors ────────────────────────────────────────────────
const C = {
  blue: "#7eb8d4",
  green: "#7ec4a0",
  lav: "#b4a4cc",
  amber: "#c9a96a",
  dim: "rgba(255,255,255,0.35)",
  border: "rgba(255,255,255,0.08)",
  bg: "rgba(255,255,255,0.03)",
};

const STYLE_COLORS: Record<string, string> = {
  curiosity: C.blue,
  suspense: C.lav,
  trending: C.amber,
  question: C.green,
  bold: "#e8a0b4",
};

const HOOK_TYPES = ["question", "shock", "mystery", "warning", "personal_story", "contrarian", "cliffhanger"];

// ─── SEO Hook Generator ───────────────────────────────────────────
function SeoHookGenerator() {
  const [title, setTitle] = useState("");
  const [plot, setPlot] = useState("");
  const [genre, setGenre] = useState("drama");
  const [audience, setAudience] = useState("general readers");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<SeoResponse | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  async function generate() {
    if (!title.trim() || !plot.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const r = await fetch("/api/brain/seo/generate-hooks", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          story_title: title,
          plot_summary: plot,
          genre,
          target_audience: audience,
        }),
      });
      const b = await r.json();
      if (!r.ok) throw new Error(b.detail ?? "Failed to generate hooks");
      setResult(b as SeoResponse);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate hooks");
    } finally {
      setLoading(false);
    }
  }

  function copy(text: string) {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(text);
      setTimeout(() => setCopied(null), 1800);
    });
  }

  const scoreBar = (score: number) => (
    <div
      style={{
        height: 3,
        borderRadius: 2,
        background: "rgba(255,255,255,0.06)",
        marginTop: 6,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${Math.round(score * 100)}%`,
          background: C.green,
          borderRadius: 2,
          transition: "width .6s ease",
        }}
      />
    </div>
  );

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <style>{`@keyframes breathe{0%,100%{opacity:.4}50%{opacity:1}}`}</style>
      {/* Input form */}
      <div
        style={{
          background: C.bg,
          border: `1px solid ${C.border}`,
          borderRadius: 12,
          padding: "20px 22px",
        }}
      >
        <div className="eyebrow" style={{ color: C.lav, marginBottom: 12 }}>
          SEO HOOK GENERATOR — BRAIN
        </div>
        <div style={{ display: "grid", gap: 12 }}>
          <div>
            <label style={{ fontSize: 12, color: C.dim, display: "block", marginBottom: 4 }}>
              Story Title
            </label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. The Last Signal"
              style={{ width: "100%", padding: "8px 12px", borderRadius: 8, border: `1px solid ${C.border}`, background: "rgba(255,255,255,0.04)", color: "#f8fafc", fontSize: 13 }}
            />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <div>
              <label style={{ fontSize: 12, color: C.dim, display: "block", marginBottom: 4 }}>Genre</label>
              <select
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                style={{ width: "100%", padding: "8px 12px", borderRadius: 8, border: `1px solid ${C.border}`, background: "#161922", color: "#f8fafc", fontSize: 13 }}
              >
                {["drama", "thriller", "romance", "sci-fi", "horror", "mystery", "action", "comedy", "documentary"].map((g) => (
                  <option key={g}>{g}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ fontSize: 12, color: C.dim, display: "block", marginBottom: 4 }}>Target Audience</label>
              <input
                value={audience}
                onChange={(e) => setAudience(e.target.value)}
                placeholder="general readers"
                style={{ width: "100%", padding: "8px 12px", borderRadius: 8, border: `1px solid ${C.border}`, background: "rgba(255,255,255,0.04)", color: "#f8fafc", fontSize: 13 }}
              />
            </div>
          </div>
          <div>
            <label style={{ fontSize: 12, color: C.dim, display: "block", marginBottom: 4 }}>Plot Summary</label>
            <textarea
              value={plot}
              onChange={(e) => setPlot(e.target.value)}
              placeholder="Briefly describe the plot, main conflict, and key turning points…"
              rows={4}
              style={{ width: "100%", padding: "8px 12px", borderRadius: 8, border: `1px solid ${C.border}`, background: "rgba(255,255,255,0.04)", color: "#f8fafc", fontSize: 13, resize: "vertical", lineHeight: 1.6 }}
            />
          </div>
          <button
            className="primary"
            disabled={loading || !title.trim() || !plot.trim()}
            onClick={generate}
            style={{ justifySelf: "start", padding: "8px 20px", fontSize: 13 }}
          >
            {loading ? "Generating…" : "Generate 5 Hooks"}
          </button>
        </div>
      </div>

      {error && <ErrorState message={error} retry={generate} />}

      {result && (
        <div style={{ display: "grid", gap: 16 }}>
          {/* Best hook highlight */}
          <div
            style={{
              background: "rgba(126,196,160,0.06)",
              border: `1px solid rgba(126,196,160,0.25)`,
              borderLeft: `3px solid ${C.green}`,
              borderRadius: "0 10px 10px 0",
              padding: "14px 18px",
            }}
          >
            <div style={{ fontSize: 11, letterSpacing: ".8px", color: C.green, marginBottom: 6 }}>
              BEST HOOK
            </div>
            <div style={{ fontSize: 16, fontWeight: 600, color: "#f8fafc", lineHeight: 1.5 }}>
              {result.best_hook}
            </div>
            <button
              onClick={() => copy(result.best_hook)}
              style={{ marginTop: 10, fontSize: 11, color: C.dim, background: "transparent", border: `1px solid ${C.border}`, borderRadius: 6, padding: "4px 10px", cursor: "pointer" }}
            >
              {copied === result.best_hook ? "Copied!" : "Copy"}
            </button>
          </div>

          {/* Hook variants */}
          <div style={{ display: "grid", gap: 10 }}>
            {result.hooks.map((h) => (
              <div
                key={h.style}
                style={{
                  background: C.bg,
                  border: `1px solid ${C.border}`,
                  borderLeft: `3px solid ${STYLE_COLORS[h.style] ?? C.dim}`,
                  borderRadius: "0 10px 10px 0",
                  padding: "12px 16px",
                  display: "grid",
                  gridTemplateColumns: "1fr auto",
                  gap: 10,
                  alignItems: "start",
                }}
              >
                <div>
                  <div style={{ fontSize: 11, color: STYLE_COLORS[h.style] ?? C.dim, letterSpacing: ".6px", marginBottom: 4 }}>
                    {h.style.toUpperCase()}
                  </div>
                  <div style={{ fontSize: 14, color: "#f8fafc", fontWeight: 500, lineHeight: 1.5 }}>
                    {h.hook_text}
                  </div>
                  <div style={{ fontSize: 11, color: C.dim, marginTop: 4 }}>{h.reasoning}</div>
                  {scoreBar(h.score)}
                  <div style={{ fontSize: 10, color: C.dim, marginTop: 4 }}>Score: {Math.round(h.score * 100)}%</div>
                </div>
                <button
                  onClick={() => copy(h.hook_text)}
                  style={{ fontSize: 11, color: C.dim, background: "transparent", border: `1px solid ${C.border}`, borderRadius: 6, padding: "4px 10px", cursor: "pointer", whiteSpace: "nowrap" }}
                >
                  {copied === h.hook_text ? "Copied!" : "Copy"}
                </button>
              </div>
            ))}
          </div>

          {/* SEO Keywords */}
          {result.seo_keywords.length > 0 && (
            <div
              style={{
                background: C.bg,
                border: `1px solid ${C.border}`,
                borderRadius: 10,
                padding: "14px 16px",
              }}
            >
              <div style={{ fontSize: 11, letterSpacing: ".8px", color: C.amber, marginBottom: 10 }}>
                SEO KEYWORDS
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {result.seo_keywords.map((kw) => (
                  <span
                    key={kw}
                    style={{
                      fontSize: 12,
                      color: "#cbd5e1",
                      background: "rgba(255,255,255,0.05)",
                      border: `1px solid ${C.border}`,
                      borderRadius: 20,
                      padding: "3px 10px",
                    }}
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Hook Library (original, preserved) ──────────────────────────
function HookLibrary() {
  const [items, setItems] = useState<HookItem[]>([]);
  const [text, setText] = useState("");
  const [type, setType] = useState("question");
  const [topic, setTopic] = useState("");
  const [error, setError] = useState("");

  async function load() {
    try {
      const r = await fetch("/api/v1/hooks", { credentials: "include" });
      const b = await r.json();
      if (!r.ok) throw new Error(b.detail ?? "Failed to load hooks");
      setItems(b as HookItem[]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load hooks");
    }
  }

  useEffect(() => { load(); }, []);

  async function add() {
    try {
      const r = await fetch("/api/v1/hooks", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hook_text: text, hook_type: type, topic: topic || null }),
      });
      const b = await r.json();
      if (!r.ok) throw new Error(b.detail ?? "Failed to add hook");
      setText("");
      setTopic("");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to add hook");
    }
  }

  return (
    <div>
      {error && <ErrorState message={error} retry={load} />}
      <div className="inline-form" style={{ marginBottom: 16 }}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Hook text" />
        <select value={type} onChange={(e) => setType(e.target.value)}>
          {HOOK_TYPES.map((x) => <option key={x}>{x}</option>)}
        </select>
        <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Topic" />
        <button className="primary" disabled={!text.trim()} onClick={add}>
          Add hook
        </button>
      </div>
      <div className="list">
        {items.map((x) => (
          <div className="list-card" key={x.id}>
            <div>
              <strong>{x.hook_text}</strong>
              <p className="muted">
                {x.hook_type} · used {x.used_count} · score {x.performance_score ?? "—"}
              </p>
            </div>
            <span className="muted">{x.is_default ? "DEFAULT" : ""}</span>
          </div>
        ))}
      </div>
      {!items.length && <div className="empty-state">No hooks yet.</div>}
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────
const TABS = ["SEO Hook Generator", "Hook Library"] as const;
type Tab = typeof TABS[number];

export default function HookLibraryPage() {
  const [tab, setTab] = useState<Tab>("SEO Hook Generator");

  return (
    <AppShell title="Hook & SEO Studio">
      {/* Tab bar */}
      <div
        style={{
          display: "flex",
          gap: 0,
          borderBottom: "1px solid rgba(255,255,255,0.07)",
          marginBottom: 20,
        }}
      >
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              background: "transparent",
              border: "none",
              borderBottom: tab === t ? `1.5px solid ${C.lav}` : "1.5px solid transparent",
              color: tab === t ? "#f8fafc" : "rgba(255,255,255,0.4)",
              fontSize: 11,
              letterSpacing: ".8px",
              textTransform: "uppercase",
              padding: "10px 18px",
              cursor: "pointer",
              transition: "color .2s",
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "SEO Hook Generator" ? (
        <SeoHookGenerator />
      ) : (
        <section className="card">
          <div className="eyebrow">HOOK LIBRARY</div>
          <p className="muted">Reusable hooks and observed performance data. Default changes remain human-controlled.</p>
          <HookLibrary />
        </section>
      )}
    </AppShell>
  );
}