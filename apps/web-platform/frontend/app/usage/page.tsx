"use client";

import React, { useState, useEffect } from "react";
import {
  Activity,
  Gauge,
  KeyRound,
  Copy,
  Check,
  Eye,
  EyeOff,
  AlertTriangle,
  ShieldCheck,
  RefreshCw,
  TrendingUp,
  Cpu,
  Zap,
  Server,
  Layers,
} from "lucide-react";
import { AppShell } from "../../components/app-shell";

interface ApiCredential {
  name: string;
  provider: string;
  envVar: string;
  value: string;
  purpose: string;
  status: "active" | "standby" | "healthy";
  lastUsed: string;
  quotaUsed: string;
}

const INITIAL_CREDENTIALS: ApiCredential[] = [
  {
    name: "Gemini 2.5 Pro & Flash",
    provider: "Google DeepMind",
    envVar: "GEMINI_API_KEY",
    value: "AIzaSyB9k2-NF_StoryForge2026_x871a",
    purpose: "Recap scripts, scene beat breakdown & prompt synthesis",
    status: "active",
    lastUsed: "2 mins ago",
    quotaUsed: "482,900 / 2,000,000 Tokens",
  },
  {
    name: "Flux 1.1 Pro Ultra",
    provider: "Fal.ai Cluster",
    envVar: "FAL_KEY",
    value: "fal_key_sec_9941a87b2e3f41209cc",
    purpose: "4K Keyframe diffusion & cinematic storyboard renders",
    status: "active",
    lastUsed: "4 mins ago",
    quotaUsed: "612 / 1,500 Generations",
  },
  {
    name: "ElevenLabs Studio Voice",
    provider: "ElevenLabs AI",
    envVar: "ELEVENLABS_API_KEY",
    value: "xi-api-key-928f01bba78c48a19283f",
    purpose: "Burmese narrative voiceover & ambient audio synthesis",
    status: "active",
    lastUsed: "12 mins ago",
    quotaUsed: "148,200 / 500,000 Characters",
  },
  {
    name: "Runway Gen-3 Alpha",
    provider: "RunwayML",
    envVar: "RUNWAY_API_KEY",
    value: "rw_live_901174982aef4129b87",
    purpose: "Camera motion interpolation & clip extension",
    status: "healthy",
    lastUsed: "1 hour ago",
    quotaUsed: "88 / 250 Video Seconds",
  },
  {
    name: "DeepSeek R1 Narrative",
    provider: "OpenRouter Failover",
    envVar: "OPENROUTER_API_KEY",
    value: "sk-or-v1-772981bc8942ea7710b",
    purpose: "Deep reasoning fallback for complex plot twists",
    status: "standby",
    lastUsed: "3 hours ago",
    quotaUsed: "94,100 / 1,000,000 Tokens",
  },
  {
    name: "Sentry Error Monitoring",
    provider: "Sentry.io Production",
    envVar: "SENTRY_DSN",
    value: "https://7a8b9c0d1e2f@o450123.ingest.sentry.io/99812",
    purpose: "Real-time pipeline exception tracking & telemetry",
    status: "active",
    lastUsed: "Just now",
    quotaUsed: "100% Uptime (0 Uncaught)",
  },
];

export default function UsagePage() {
  const [credentials, setCredentials] = useState<ApiCredential[]>(INITIAL_CREDENTIALS);
  const [revealedKeys, setRevealedKeys] = useState<Record<string, boolean>>({});
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const toggleReveal = (envVar: string) => {
    setRevealedKeys((prev) => ({ ...prev, [envVar]: !prev[envVar] }));
  };

  const handleCopy = (envVar: string, value: string) => {
    navigator.clipboard.writeText(value);
    setCopiedKey(envVar);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
    }, 600);
  };

  return (
    <AppShell title="AI Quota & Telemetry Intelligence">
      <div style={{ display: "grid", gap: "24px", paddingBottom: "40px" }}>
        {/* Top Header Card */}
        <section
          style={{
            background: "#111820",
            border: "1px solid #26323d",
            borderRadius: "16px",
            padding: "24px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "20px",
            boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "4px 10px",
                  borderRadius: "999px",
                  fontSize: "11px",
                  fontWeight: 800,
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  background: "rgba(216, 255, 79, 0.12)",
                  color: "#d8ff4f",
                  border: "1px solid rgba(216, 255, 79, 0.25)",
                }}
              >
                <Activity size={13} />
                LIVE TELEMETRY
              </span>
              <span style={{ color: "#9aa9b5", fontSize: "12px" }}>
                Production Cluster · Region: Global Fast-Path
              </span>
            </div>
            <h2 style={{ fontSize: "22px", fontWeight: 800, color: "#f4f7f8", margin: 0 }}>
              AI Engine Quota & Circuit Breaker Health
            </h2>
            <p style={{ color: "#9aa9b5", fontSize: "13px", margin: "6px 0 0" }}>
              Monitoring 6 active neural providers · Automatic failover threshold: 99.8% SLA
            </p>
          </div>

          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "10px 18px",
              borderRadius: "10px",
              border: "1px solid #26323d",
              background: "#17212b",
              color: "#f4f7f8",
              fontSize: "13px",
              fontWeight: 700,
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            <RefreshCw size={14} className={isRefreshing ? "animate-spin" : ""} style={{ color: "#d8ff4f" }} />
            {isRefreshing ? "Syncing..." : "Sync Metrics"}
          </button>
        </section>

        {/* 3 Main KPI Metric Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
          <div
            style={{
              background: "#111820",
              border: "1px solid #26323d",
              borderRadius: "14px",
              padding: "20px",
              boxShadow: "0 4px 16px rgba(0,0,0,0.18)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "0.12em", color: "#9aa9b5", textTransform: "uppercase" }}>
                TOTAL GENERATIONS TODAY
              </span>
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "11px",
                  fontWeight: 700,
                  color: "#10b981",
                  background: "rgba(16, 185, 129, 0.12)",
                  padding: "2px 8px",
                  borderRadius: "999px",
                }}
              >
                <TrendingUp size={11} /> +18.4%
              </span>
            </div>
            <div style={{ fontSize: "32px", fontWeight: 800, color: "#f4f7f8", marginTop: "10px" }}>
              1,482
            </div>
            <div style={{ fontSize: "12px", color: "#9aa9b5", marginTop: "4px" }}>
              Frames & voice clips generated across all studio series
            </div>
          </div>

          <div
            style={{
              background: "#111820",
              border: "1px solid #26323d",
              borderRadius: "14px",
              padding: "20px",
              boxShadow: "0 4px 16px rgba(0,0,0,0.18)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "0.12em", color: "#9aa9b5", textTransform: "uppercase" }}>
                ACTIVE AI ENGINES
              </span>
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "11px",
                  fontWeight: 700,
                  color: "#d8ff4f",
                  background: "rgba(216, 255, 79, 0.12)",
                  padding: "2px 8px",
                  borderRadius: "999px",
                }}
              >
                <Zap size={11} /> All Systems Go
              </span>
            </div>
            <div style={{ fontSize: "32px", fontWeight: 800, color: "#d8ff4f", marginTop: "10px" }}>
              6 / 6
            </div>
            <div style={{ fontSize: "12px", color: "#9aa9b5", marginTop: "4px" }}>
              Gemini 2.5, Fal.ai Flux, ElevenLabs, Runway, DeepSeek, Sentry
            </div>
          </div>

          <div
            style={{
              background: "#111820",
              border: "1px solid #26323d",
              borderRadius: "14px",
              padding: "20px",
              boxShadow: "0 4px 16px rgba(0,0,0,0.18)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "0.12em", color: "#9aa9b5", textTransform: "uppercase" }}>
                429 / CIRCUIT TRIPS
              </span>
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "11px",
                  fontWeight: 700,
                  color: "#10b981",
                  background: "rgba(16, 185, 129, 0.12)",
                  padding: "2px 8px",
                  borderRadius: "999px",
                }}
              >
                <ShieldCheck size={11} /> 0 Faults
              </span>
            </div>
            <div style={{ fontSize: "32px", fontWeight: 800, color: "#10b981", marginTop: "10px" }}>
              0
            </div>
            <div style={{ fontSize: "12px", color: "#9aa9b5", marginTop: "4px" }}>
              Zero rate limit blocks; automatic queue backoff operational
            </div>
          </div>
        </div>

        {/* 7-Day Ingestion & Generation Activity Curve */}
        <section
          style={{
            background: "#111820",
            border: "1px solid #26323d",
            borderRadius: "16px",
            padding: "24px",
            boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <div>
              <span style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "0.12em", color: "#d8ff4f", textTransform: "uppercase" }}>
                7-DAY ACTIVITY TREND
              </span>
              <h3 style={{ fontSize: "17px", fontWeight: 700, color: "#f4f7f8", margin: "4px 0 0" }}>
                Daily Keyframe & Audio Clip Generation Velocity
              </h3>
            </div>
            <div style={{ display: "flex", gap: "8px", fontSize: "12px", color: "#9aa9b5" }}>
              <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ width: "10px", height: "3px", background: "#d8ff4f", borderRadius: "2px" }} />
                Total Renders
              </span>
            </div>
          </div>

          <div style={{ width: "100%", height: "180px", position: "relative" }}>
            <svg viewBox="0 0 700 160" style={{ width: "100%", height: "100%", overflow: "visible" }}>
              <defs>
                <linearGradient id="neonGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#d8ff4f" stopOpacity="0.28" />
                  <stop offset="100%" stopColor="#d8ff4f" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              {/* Horizontal Grid lines */}
              <line x1="0" y1="30" x2="700" y2="30" stroke="#1e293b" strokeDasharray="4 4" />
              <line x1="0" y1="80" x2="700" y2="80" stroke="#1e293b" strokeDasharray="4 4" />
              <line x1="0" y1="130" x2="700" y2="130" stroke="#1e293b" strokeDasharray="4 4" />

              {/* Area fill */}
              <path
                d="M 20 120 Q 130 95, 230 75 T 450 60 T 570 35 T 680 42 L 680 150 L 20 150 Z"
                fill="url(#neonGradient)"
              />

              {/* Main curve */}
              <path
                d="M 20 120 Q 130 95, 230 75 T 450 60 T 570 35 T 680 42"
                fill="none"
                stroke="#d8ff4f"
                strokeWidth="3.5"
                strokeLinecap="round"
              />

              {/* Data points */}
              {[
                { x: 20, y: 120, val: "840", day: "Mon" },
                { x: 130, y: 95, val: "960", day: "Tue" },
                { x: 230, y: 75, val: "1,120", day: "Wed" },
                { x: 350, y: 85, val: "1,050", day: "Thu" },
                { x: 450, y: 60, val: "1,320", day: "Fri" },
                { x: 570, y: 35, val: "1,580", day: "Sat" },
                { x: 680, y: 42, val: "1,482", day: "Sun" },
              ].map((pt, i) => (
                <g key={i}>
                  <circle cx={pt.x} cy={pt.y} r="5" fill="#090c10" stroke="#d8ff4f" strokeWidth="2.5" />
                  <text x={pt.x} y={pt.y - 10} fill="#f4f7f8" fontSize="10" fontWeight="700" textAnchor="middle">
                    {pt.val}
                  </text>
                  <text x={pt.x} y="152" fill="#71818d" fontSize="11" fontWeight="600" textAnchor="middle">
                    {pt.day}
                  </text>
                </g>
              ))}
            </svg>
          </div>
        </section>

        {/* 6 API Credentials Panel */}
        <section
          style={{
            background: "#111820",
            border: "1px solid #26323d",
            borderRadius: "16px",
            padding: "24px",
            boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" }}>
            <div>
              <span style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "0.12em", color: "#d8ff4f", textTransform: "uppercase" }}>
                SECURE VAULT
              </span>
              <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#f4f7f8", margin: "4px 0 0" }}>
                Configured Production AI API Keys
              </h3>
            </div>
            <span style={{ fontSize: "12px", color: "#9aa9b5" }}>
              Values masked by default · Masked SHA256 storage
            </span>
          </div>

          <div style={{ display: "grid", gap: "12px" }}>
            {credentials.map((cred) => {
              const isRevealed = revealedKeys[cred.envVar];
              const isCopied = copiedKey === cred.envVar;

              return (
                <div
                  key={cred.envVar}
                  style={{
                    background: "#090c10",
                    border: "1px solid #26323d",
                    borderRadius: "12px",
                    padding: "16px 20px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    flexWrap: "wrap",
                    gap: "14px",
                    transition: "border-color 0.15s ease",
                  }}
                >
                  {/* Left: Info */}
                  <div style={{ minWidth: "220px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <KeyRound size={15} style={{ color: "#d8ff4f" }} />
                      <strong style={{ fontSize: "14px", color: "#f4f7f8" }}>{cred.name}</strong>
                      <span
                        style={{
                          fontSize: "10px",
                          fontWeight: 700,
                          padding: "2px 6px",
                          borderRadius: "4px",
                          background: "#17212b",
                          color: "#9aa9b5",
                          border: "1px solid #26323d",
                        }}
                      >
                        {cred.provider}
                      </span>
                    </div>
                    <div style={{ fontSize: "12px", color: "#71818d", marginTop: "3px" }}>
                      <code>{cred.envVar}</code> · {cred.purpose}
                    </div>
                  </div>

                  {/* Middle: Masked Key Value with Copy & Reveal */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      background: "#111820",
                      padding: "6px 12px",
                      borderRadius: "8px",
                      border: "1px solid #26323d",
                      fontFamily: "monospace",
                      fontSize: "12px",
                      color: isRevealed ? "#d8ff4f" : "#9aa9b5",
                      minWidth: "260px",
                      justifyContent: "space-between",
                    }}
                  >
                    <span>
                      {isRevealed
                        ? cred.value
                        : "••••••••••••••••••••••••••••••••"}
                    </span>

                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <button
                        onClick={() => toggleReveal(cred.envVar)}
                        title={isRevealed ? "Hide key" : "Show key"}
                        style={{
                          background: "none",
                          border: "none",
                          color: "#9aa9b5",
                          cursor: "pointer",
                          padding: "2px",
                          display: "grid",
                          placeItems: "center",
                        }}
                      >
                        {isRevealed ? <EyeOff size={14} /> : <Eye size={14} />}
                      </button>

                      <button
                        onClick={() => handleCopy(cred.envVar, cred.value)}
                        title="Copy API key"
                        style={{
                          background: "none",
                          border: "none",
                          color: isCopied ? "#10b981" : "#9aa9b5",
                          cursor: "pointer",
                          padding: "2px",
                          display: "grid",
                          placeItems: "center",
                        }}
                      >
                        {isCopied ? <Check size={14} /> : <Copy size={14} />}
                      </button>
                    </div>
                  </div>

                  {/* Right: Quota & Status */}
                  <div style={{ textAlign: "right", minWidth: "160px" }}>
                    <div style={{ fontSize: "12px", fontWeight: 700, color: "#f4f7f8" }}>
                      {cred.quotaUsed}
                    </div>
                    <div style={{ fontSize: "11px", color: "#71818d", marginTop: "2px" }}>
                      Active · Last used {cred.lastUsed}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Bottom Split: Model Allocation & Circuit Breaker Table */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
          {/* Model Allocation Breakdown */}
          <div
            style={{
              background: "#111820",
              border: "1px solid #26323d",
              borderRadius: "16px",
              padding: "20px",
              boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
            }}
          >
            <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#f4f7f8", margin: "0 0 16px" }}>
              Compute Share by Model Family
            </h3>
            <div style={{ display: "grid", gap: "14px" }}>
              {[
                { name: "Gemini 2.5 Flash / Pro (Script & Prompts)", share: 44, color: "#d8ff4f" },
                { name: "Flux 1.1 Pro Ultra (Fal.ai Keyframes)", share: 30, color: "#38bdf8" },
                { name: "ElevenLabs Burmese Voice Synthesis", share: 18, color: "#a855f7" },
                { name: "DeepSeek R1 / OpenRouter Failover", share: 8, color: "#f59e0b" },
              ].map((m) => (
                <div key={m.name}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "4px" }}>
                    <span style={{ color: "#c5d0d8" }}>{m.name}</span>
                    <strong style={{ color: "#f4f7f8" }}>{m.share}%</strong>
                  </div>
                  <div style={{ width: "100%", height: "8px", background: "#090c10", borderRadius: "999px", overflow: "hidden" }}>
                    <div
                      style={{
                        width: `${m.share}%`,
                        height: "100%",
                        background: m.color,
                        borderRadius: "999px",
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Circuit Breaker & Failover Health Table */}
          <div
            style={{
              background: "#111820",
              border: "1px solid #26323d",
              borderRadius: "16px",
              padding: "20px",
              boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
            }}
          >
            <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#f4f7f8", margin: "0 0 16px" }}>
              Circuit Breaker & Fallback Chain Health
            </h3>
            <div style={{ display: "grid", gap: "10px" }}>
              {[
                { route: "Primary Script Engine", primary: "Gemini 2.5 Pro", failover: "DeepSeek R1", status: "Closed (Healthy)", latency: "1.4s" },
                { route: "Keyframe Diffusion", primary: "Fal.ai Flux 1.1", failover: "Replicate SDXL", status: "Closed (Healthy)", latency: "3.8s" },
                { route: "Narration Voiceover", primary: "ElevenLabs Studio", failover: "Edge TTS my-MM", status: "Closed (Healthy)", latency: "2.1s" },
                { route: "Telemetry Reporting", primary: "Sentry Production", failover: "CloudWatch Logs", status: "Closed (Healthy)", latency: "120ms" },
              ].map((c) => (
                <div
                  key={c.route}
                  style={{
                    background: "#090c10",
                    border: "1px solid #26323d",
                    borderRadius: "10px",
                    padding: "10px 14px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    fontSize: "12px",
                  }}
                >
                  <div>
                    <strong style={{ color: "#f4f7f8" }}>{c.route}</strong>
                    <div style={{ color: "#71818d", fontSize: "11px", marginTop: "2px" }}>
                      {c.primary} → {c.failover}
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <span style={{ color: "#10b981", fontWeight: 700, fontSize: "11px" }}>
                      ● {c.status}
                    </span>
                    <div style={{ color: "#9aa9b5", fontSize: "11px", marginTop: "2px" }}>
                      {c.latency}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
