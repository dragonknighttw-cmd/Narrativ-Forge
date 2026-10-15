"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../components/app-shell";

interface ProviderStat {
  configured: boolean;
  status: string;
  calls_today: number;
  total_calls: number;
  errors_today: number;
  last_used: string | null;
}

interface UsageSummary {
  project: string;
  timestamp: string;
  date: string;
  total_calls_today: number;
  active_chains: {
    chat_priority: string[];
    rag_priority: string[];
  };
  providers: Record<string, ProviderStat>;
}

export default function UsagePage() {
  const [data, setData] = useState<UsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsage = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/ai/usage", { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch usage`);
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to load usage data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchUsage();
  }, []);

  const providers = data?.providers ? Object.entries(data.providers) : [];
  const activeCount = providers.filter(([_, p]) => p.status === "active").length;
  const errorCount = providers.reduce((sum, [_, p]) => sum + (p.errors_today || 0), 0);

  return (
    <AppShell title="AI Key Usage & Failover Health">
      <div className="ds-stack" style={{ gap: "24px" }}>
        {/* Top Metric Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
          <div className="ds-card" style={{ padding: "20px" }}>
            <div className="eyebrow">TOTAL REQUESTS TODAY</div>
            <div style={{ fontSize: "28px", fontWeight: 700, marginTop: "8px", color: "#f8fafc" }}>
              {loading ? "..." : (data?.total_calls_today ?? 0).toLocaleString()}
            </div>
            <div style={{ fontSize: "12px", color: "#64748b", marginTop: "4px" }}>Across all fallback models</div>
          </div>

          <div className="ds-card" style={{ padding: "20px" }}>
            <div className="eyebrow">ACTIVE PROVIDERS</div>
            <div style={{ fontSize: "28px", fontWeight: 700, marginTop: "8px", color: "#38bdf8" }}>
              {loading ? "..." : `${activeCount} / ${providers.length}`}
            </div>
            <div style={{ fontSize: "12px", color: "#64748b", marginTop: "4px" }}>Configured & operational</div>
          </div>

          <div className="ds-card" style={{ padding: "20px" }}>
            <div className="eyebrow">429 / QUOTA ERRORS</div>
            <div style={{ fontSize: "28px", fontWeight: 700, marginTop: "8px", color: errorCount > 0 ? "#f43f5e" : "#10b981" }}>
              {loading ? "..." : errorCount}
            </div>
            <div style={{ fontSize: "12px", color: "#64748b", marginTop: "4px" }}>Auto-switch triggered</div>
          </div>

          <div className="ds-card" style={{ padding: "20px" }}>
            <div className="eyebrow">TELEGRAM DIRECT ALERT</div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "12px" }}>
              <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#10b981" }} />
              <span style={{ fontSize: "16px", fontWeight: 600, color: "#10b981" }}>Native Trigger: Live</span>
            </div>
            <div style={{ fontSize: "12px", color: "#64748b", marginTop: "8px" }}>Topic #Narrativ-Forge</div>
          </div>
        </div>

        {error && (
          <div style={{ padding: "12px 16px", borderRadius: "12px", backgroundColor: "rgba(244,63,94,0.1)", border: "1px solid rgba(244,63,94,0.3)", color: "#f43f5e", fontSize: "13px" }}>
            ⚠️ {error} — Serving local tracking fallback
          </div>
        )}

        {/* Resilience Failover Blueprint */}
        <div className="ds-card" style={{ padding: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <div>
              <div className="eyebrow">AUTO-FAILOVER ARCHITECTURE</div>
              <h2 style={{ fontSize: "16px", fontWeight: 600, color: "#f8fafc", marginTop: "4px" }}>
                Active Multi-Provider Resilience Chains
              </h2>
            </div>
            <button
              type="button"
              onClick={() => void fetchUsage()}
              className="ds-button"
              style={{ padding: "6px 14px", fontSize: "12px", cursor: "pointer" }}
            >
              🔄 Refresh Usage
            </button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "16px" }}>
            <div style={{ padding: "16px", borderRadius: "12px", backgroundColor: "#0b1424", border: "1px solid #1e293b" }}>
              <div style={{ fontSize: "13px", fontWeight: 600, color: "#93c5fd", marginBottom: "8px" }}>
                1. Chat & Script Generation Chain
              </div>
              <div style={{ fontSize: "12px", color: "#94a3b8", lineHeight: 1.6 }}>
                <span style={{ color: "#38bdf8", fontWeight: 600 }}>Gemini 2.5/3.5</span> &rarr; Groq (Qwen-27B) &rarr; Cloudflare (Llama-3.1-8B) &rarr; Cohere &rarr; OpenRouter &rarr; NVIDIA
              </div>
            </div>

            <div style={{ padding: "16px", borderRadius: "12px", backgroundColor: "#0b1424", border: "1px solid #1e293b" }}>
              <div style={{ fontSize: "13px", fontWeight: 600, color: "#93c5fd", marginBottom: "8px" }}>
                2. Whisper STT Transcription Chain
              </div>
              <div style={{ fontSize: "12px", color: "#94a3b8", lineHeight: 1.6 }}>
                <span style={{ color: "#38bdf8", fontWeight: 600 }}>Cloudflare Whisper</span> &rarr; Groq Whisper Large-v3 &rarr; Local Celery FFmpeg fallback
              </div>
            </div>

            <div style={{ padding: "16px", borderRadius: "12px", backgroundColor: "#0b1424", border: "1px solid #1e293b" }}>
              <div style={{ fontSize: "13px", fontWeight: 600, color: "#93c5fd", marginBottom: "8px" }}>
                3. RAG Knowledge & Embedding Chain (512-D)
              </div>
              <div style={{ fontSize: "12px", color: "#94a3b8", lineHeight: 1.6 }}>
                <span style={{ color: "#38bdf8", fontWeight: 600 }}>Voyage AI (voyage-3-lite)</span> &rarr; Cohere (embed-v4.0) fallback
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Provider Usage Table */}
        <div className="ds-card" style={{ padding: "24px" }}>
          <div className="eyebrow">PROVIDER METRICS & HEALTH</div>
          <h2 style={{ fontSize: "16px", fontWeight: 600, color: "#f8fafc", marginTop: "4px", marginBottom: "16px" }}>
            Real-Time Key Usage & Error Tracking
          </h2>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px", textAlign: "left" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid #1e293b", color: "#64748b" }}>
                  <th style={{ padding: "10px 14px" }}>Provider</th>
                  <th style={{ padding: "10px 14px" }}>Status</th>
                  <th style={{ padding: "10px 14px", textAlign: "right" }}>Calls Today</th>
                  <th style={{ padding: "10px 14px", textAlign: "right" }}>Total Calls</th>
                  <th style={{ padding: "10px 14px", textAlign: "right" }}>429 Errors</th>
                  <th style={{ padding: "10px 14px" }}>Failover Action</th>
                </tr>
              </thead>
              <tbody>
                {providers.map(([name, stat]) => {
                  const isExhausted = stat.status.includes("exhausted");
                  const isActive = stat.status === "active";
                  return (
                    <tr key={name} style={{ borderBottom: "1px solid #1e293b" }}>
                      <td style={{ padding: "12px 14px", fontWeight: 600, color: "#f8fafc", textTransform: "capitalize" }}>
                        {name}
                      </td>
                      <td style={{ padding: "12px 14px" }}>
                        <span
                          style={{
                            padding: "3px 8px",
                            borderRadius: "6px",
                            fontSize: "11px",
                            fontWeight: 600,
                            backgroundColor: isActive
                              ? "rgba(16, 185, 129, 0.12)"
                              : isExhausted
                              ? "rgba(244, 63, 94, 0.12)"
                              : "rgba(100, 116, 139, 0.12)",
                            color: isActive ? "#34d399" : isExhausted ? "#fb7185" : "#94a3b8",
                            border: `1px solid ${isActive ? "rgba(16, 185, 129, 0.3)" : isExhausted ? "rgba(244, 63, 94, 0.3)" : "rgba(100, 116, 139, 0.3)"}`,
                          }}
                        >
                          {stat.status}
                        </span>
                      </td>
                      <td style={{ padding: "12px 14px", textAlign: "right", fontFamily: "monospace", color: "#e2e8f0" }}>
                        {stat.calls_today}
                      </td>
                      <td style={{ padding: "12px 14px", textAlign: "right", fontFamily: "monospace", color: "#94a3b8" }}>
                        {stat.total_calls}
                      </td>
                      <td style={{ padding: "12px 14px", textAlign: "right", fontFamily: "monospace", color: stat.errors_today > 0 ? "#f43f5e" : "#64748b" }}>
                        {stat.errors_today}
                      </td>
                      <td style={{ padding: "12px 14px", fontSize: "12px", color: "#94a3b8" }}>
                        {isExhausted ? "Trigger Telegram & Failover" : "Operational"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
