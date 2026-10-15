"use client";
import Link from "next/link";
import { AppShell } from "../../components/app-shell";
import { useEffect, useState } from "react";

// ─── Brain Soul mini-status ───────────────────────────────────────
const BC = {
  lav: "#b4a4cc",
  green: "#7ec4a0",
  blue: "#7eb8d4",
  amber: "#c9a96a",
  border: "rgba(255,255,255,0.08)",
  dim: "rgba(255,255,255,0.3)",
};

function fmtD(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

interface BrainSoulStatus {
  total_syntheses?: number;
  soul_file_entries?: number;
  latest_synthesis_period?: string;
  latest_synthesis_at?: string;
  latest_synthesis_snippet?: string;
}

function BrainSoulMini() {
  const [data, setData] = useState<BrainSoulStatus | null>(null);

  useEffect(() => {
    fetch("/api/brain/soul/status", { credentials: "include" })
      .then((r) => r.json())
      .then((d) => setData(d as BrainSoulStatus))
      .catch(() => {});
  }, []);

  return (
    <section
      style={{
        background: "rgba(22,25,34,0.85)",
        border: `1px solid ${BC.border}`,
        borderRadius: 12,
        padding: "18px 22px",
        marginTop: 18,
        display: "grid",
        gridTemplateColumns: "1fr auto",
        gap: 16,
        alignItems: "center",
      }}
    >
      <style>{`@keyframes breathe{0%,100%{opacity:.4}50%{opacity:1}}`}</style>
      <div>
        <div style={{ fontSize: 11, letterSpacing: ".8px", textTransform: "uppercase", color: BC.lav, marginBottom: 6 }}>
          <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: "50%", background: BC.lav, marginRight: 6, animation: "breathe 4s ease-in-out infinite" }} />
          Brain Soul Layer
        </div>
        <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
          <div>
            <div style={{ fontSize: 10, color: BC.dim }}>Syntheses</div>
            <div style={{ fontSize: 20, fontWeight: 700, color: BC.green }}>{data?.total_syntheses ?? "—"}</div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: BC.dim }}>Soul Entries</div>
            <div style={{ fontSize: 20, fontWeight: 700, color: BC.blue }}>{data?.soul_file_entries ?? "—"}</div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: BC.dim }}>Last Period</div>
            <div style={{ fontSize: 14, fontWeight: 600, color: BC.lav, marginTop: 2 }}>{data?.latest_synthesis_period ?? "—"}</div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: BC.dim }}>Last Synth</div>
            <div style={{ fontSize: 12, color: BC.dim, marginTop: 2 }}>{fmtD(data?.latest_synthesis_at ?? null)}</div>
          </div>
        </div>
        {data?.latest_synthesis_snippet && (
          <div style={{ marginTop: 10, fontSize: 11, color: "#94a3b8", borderLeft: `2px solid ${BC.lav}`, paddingLeft: 10, lineHeight: 1.6 }}>
            {data.latest_synthesis_snippet.slice(0, 180)}{(data.latest_synthesis_snippet.length ?? 0) > 180 ? "…" : ""}
          </div>
        )}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8, alignItems: "flex-end" }}>
        <Link href="/hooks" className="primary" style={{ padding: "6px 14px", fontSize: 12, whiteSpace: "nowrap" }}>
          SEO Hook Generator
        </Link>
        <button
          onClick={async () => {
            await fetch("/api/brain/soul/synthesize", { method: "POST", credentials: "include" });
          }}
          style={{ fontSize: 11, color: BC.green, cursor: "pointer", background: "transparent", border: "none", padding: "4px 0" }}
        >
          Synthesize Now
        </button>
      </div>
    </section>
  );
}

export default function DashboardPage() {
  return (
    <AppShell title="Studio Overview">
      {/* Top Banner */}
      <section className="card" style={{ background: "linear-gradient(135deg, rgba(15, 22, 38, 0.95), rgba(22, 32, 52, 0.6))", border: "1px solid var(--border)", padding: "26px" }}>
        <div className="eyebrow" style={{ color: "#38bdf8" }}>PRODUCTION COMMAND CENTER</div>
        <h2 style={{ fontSize: "24px", fontWeight: "700", marginTop: "6px", marginBottom: "8px" }}>Burmese Short-Form Video Studio</h2>
        <p className="muted" style={{ maxWidth: "780px" }}>
          Production pipeline from concept ideation to Gemini Burmese scripting, Groq scene hooks, Groq Whisper subtitle generation, and automated Google Drive master exports.
        </p>
      </section>

      {/* Brain Soul Mini Status */}
      <BrainSoulMini />

      {/* KPI Stats Grid */}
      <div className="grid" style={{ marginTop: "18px" }}>
        <div className="card" style={{ padding: "18px" }}>
          <div className="eyebrow">ACTIVE WORKFLOWS</div>
          <div className="metric" style={{ fontSize: "28px", color: "#f8fafc" }}>12</div>
          <div className="muted" style={{ fontSize: "12px" }}>Episodes in production queue</div>
        </div>
        <div className="card" style={{ padding: "18px" }}>
          <div className="eyebrow">AI SCRIPT ENGINE</div>
          <div className="status" style={{ fontSize: "16px", color: "#38bdf8" }}>Gemini 2.5/3.5</div>
          <div className="muted" style={{ fontSize: "12px" }}>Fallback: Groq Qwen-3.8-27b</div>
        </div>
        <div className="card" style={{ padding: "18px" }}>
          <div className="eyebrow">SUBTITLE STT</div>
          <div className="status" style={{ fontSize: "16px", color: "#10b981" }}>Groq Whisper</div>
          <div className="muted" style={{ fontSize: "12px" }}>&lt; 2s transcription latency</div>
        </div>
        <div className="card" style={{ padding: "18px" }}>
          <div className="eyebrow">TELEGRAM REVIEW</div>
          <div className="status" style={{ fontSize: "16px", color: "#10b981" }}>Active &amp; Ready</div>
          <div className="muted" style={{ fontSize: "12px" }}>Direct Supergroup dispatch</div>
        </div>
      </div>

      {/* Studio Quick Actions & Fallback Health */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "18px", marginTop: "18px" }}>
        <section className="card" style={{ padding: "22px" }}>
          <div className="eyebrow">END-TO-END PIPELINE</div>
          <h3 style={{ fontSize: "18px", fontWeight: "600", margin: "8px 0 16px 0" }}>Pipeline Stages &amp; Quick Access</h3>
          <div style={{ display: "grid", gap: "12px" }}>
            {[
              { step: "1. Ideas & Hook Generation", desc: "Viral opening lines & content angles", href: "/ideas", label: "Open Ideas" },
              { step: "2. Burmese Script Studio", desc: "AI dialogue writing with scene-by-scene timing", href: "/episodes", label: "Open Episodes" },
              { step: "3. Subtitle Studio & Audio Transcribe", desc: "Burmese syllable normalization & Whisper VTT", href: "/subtitles", label: "Open Subtitles" },
              { step: "4. Production Review & Telegram Approval", desc: "Producer review, quality check, and cloud export", href: "/review", label: "Open Review" },
            ].map(({ step, desc, href, label }) => (
              <div key={step} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", background: "var(--color-bg-inset)", border: "1px solid var(--border)", borderRadius: "8px" }}>
                <div>
                  <strong style={{ fontSize: "14px", display: "block" }}>{step}</strong>
                  <span className="muted" style={{ fontSize: "12px" }}>{desc}</span>
                </div>
                <Link href={href} className="primary" style={{ padding: "6px 14px", fontSize: "12px" }}>{label}</Link>
              </div>
            ))}
          </div>
        </section>

        <section className="card" style={{ padding: "22px" }}>
          <div className="eyebrow">AI RESILIENCE CHAIN</div>
          <h3 style={{ fontSize: "18px", fontWeight: "600", margin: "8px 0 16px 0" }}>Active Fallback Chain</h3>
          <div style={{ display: "grid", gap: "10px", fontSize: "13px" }}>
            {[
              { label: "Chat 1:", value: "Gemini 2.5/3.5-flash", color: "#38bdf8" },
              { label: "Chat 2 (Fallback):", value: "Groq Qwen-3.8-27b", color: "#f8fafc" },
              { label: "Chat 3 (Free):", value: "Cloudflare Llama-3.1", color: "#f8fafc" },
              { label: "RAG Vector 1:", value: "Voyage AI (512-D)", color: "#10b981" },
              { label: "RAG Vector 2:", value: "Cohere embed-v4.0", color: "#f8fafc" },
            ].map(({ label, value, color }, i, arr) => (
              <div key={label} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: i < arr.length - 1 ? "1px solid var(--border)" : "none" }}>
                <span className="muted">{label}</span>
                <span style={{ color, fontWeight: color === "#f8fafc" ? 500 : 600 }}>{value}</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: "20px", padding: "12px", background: "rgba(56, 189, 248, 0.06)", border: "1px solid rgba(56, 189, 248, 0.2)", borderRadius: "8px", fontSize: "12px", color: "#94a3b8" }}>
            Telegram မှ <code>/ai_status</code> ရိုက်ပို့၍ live usage စစ်ဆေးနိုင်ပါသည်။
          </div>
        </section>
      </div>
    </AppShell>
  );
}
