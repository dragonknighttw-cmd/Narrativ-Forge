import Link from "next/link";
import { AppShell } from "../../components/app-shell";

export default function DashboardPage() {
  return (
    <AppShell title="Studio Overview">
      {/* Top Banner / Studio Status */}
      <section className="card" style={{ background: "linear-gradient(135deg, rgba(15, 22, 38, 0.95), rgba(22, 32, 52, 0.6))", border: "1px solid var(--border)", padding: "26px" }}>
        <div className="eyebrow" style={{ color: "#38bdf8" }}>PRODUCTION COMMAND CENTER</div>
        <h2 style={{ fontSize: "24px", fontWeight: "700", marginTop: "6px", marginBottom: "8px" }}>Burmese Short-Form Video Studio</h2>
        <p className="muted" style={{ maxWidth: "780px" }}>
          Production pipeline from concept ideation to Gemini Burmese scripting, Groq scene hooks, Groq Whisper subtitle generation, and automated Google Drive master exports.
        </p>
      </section>

      {/* KPI Stats Grid */}
      <div className="grid" style={{ marginTop: "18px" }}>
        <div className="card" style={{ padding: "18px" }}>
          <div className="eyebrow">ACTIVE WORKFLOWS</div>
          <div className="metric" style={{ fontSize: "28px", color: "#f8fafc" }}>12</div>
          <div className="muted" style={{ fontSize: "12px" }}>Episodes in production queue</div>
        </div>
        <div className="card" style={{ padding: "18px" }}>
          <div className="eyebrow">AI SCRIPT ENGINE</div>
          <div className="status" style={{ fontSize: "16px", color: "#38bdf8" }}>🥇 Gemini 2.5/3.5</div>
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
        {/* Production Stage Pipeline */}
        <section className="card" style={{ padding: "22px" }}>
          <div className="eyebrow">END-TO-END PIPELINE</div>
          <h3 style={{ fontSize: "18px", fontWeight: "600", margin: "8px 0 16px 0" }}>Pipeline Stages &amp; Quick Access</h3>
          
          <div style={{ display: "grid", gap: "12px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", background: "var(--color-bg-inset)", border: "1px solid var(--border)", borderRadius: "8px" }}>
              <div>
                <strong style={{ fontSize: "14px", display: "block" }}>1. Ideas &amp; Hook Generation</strong>
                <span className="muted" style={{ fontSize: "12px" }}>Viral opening lines &amp; content angles</span>
              </div>
              <Link href="/ideas" className="primary" style={{ padding: "6px 14px", fontSize: "12px" }}>Open Ideas</Link>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", background: "var(--color-bg-inset)", border: "1px solid var(--border)", borderRadius: "8px" }}>
              <div>
                <strong style={{ fontSize: "14px", display: "block" }}>2. Burmese Script Studio</strong>
                <span className="muted" style={{ fontSize: "12px" }}>AI dialogue writing with scene-by-scene timing</span>
              </div>
              <Link href="/episodes" className="primary" style={{ padding: "6px 14px", fontSize: "12px" }}>Open Episodes</Link>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", background: "var(--color-bg-inset)", border: "1px solid var(--border)", borderRadius: "8px" }}>
              <div>
                <strong style={{ fontSize: "14px", display: "block" }}>3. Subtitle Studio &amp; Audio Transcribe</strong>
                <span className="muted" style={{ fontSize: "12px" }}>Burmese syllable normalization &amp; Whisper VTT</span>
              </div>
              <Link href="/subtitles" className="primary" style={{ padding: "6px 14px", fontSize: "12px" }}>Open Subtitles</Link>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", background: "var(--color-bg-inset)", border: "1px solid var(--border)", borderRadius: "8px" }}>
              <div>
                <strong style={{ fontSize: "14px", display: "block" }}>4. Production Review &amp; Telegram Approval</strong>
                <span className="muted" style={{ fontSize: "12px" }}>Producer review, quality check, and cloud export</span>
              </div>
              <Link href="/review" className="primary" style={{ padding: "6px 14px", fontSize: "12px" }}>Open Review</Link>
            </div>
          </div>
        </section>

        {/* AI Health & Fallback Card */}
        <section className="card" style={{ padding: "22px" }}>
          <div className="eyebrow">AI RESILIENCE CHAIN</div>
          <h3 style={{ fontSize: "18px", fontWeight: "600", margin: "8px 0 16px 0" }}>Active Fallback Chain</h3>
          
          <div style={{ display: "grid", gap: "10px", fontSize: "13px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
              <span className="muted">Chat 1:</span>
              <span style={{ color: "#38bdf8", fontWeight: "600" }}>Gemini 2.5/3.5-flash</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
              <span className="muted">Chat 2 (Fallback):</span>
              <span style={{ color: "#f8fafc", fontWeight: "500" }}>Groq Qwen-3.8-27b</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
              <span className="muted">Chat 3 (Free):</span>
              <span style={{ color: "#f8fafc", fontWeight: "500" }}>Cloudflare Llama-3.1</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
              <span className="muted">RAG Vector 1:</span>
              <span style={{ color: "#10b981", fontWeight: "500" }}>Voyage AI (512-D)</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0" }}>
              <span className="muted">RAG Vector 2:</span>
              <span style={{ color: "#f8fafc", fontWeight: "500" }}>Cohere embed-v4.0</span>
            </div>
          </div>

          <div style={{ marginTop: "20px", padding: "12px", background: "rgba(56, 189, 248, 0.06)", border: "1px solid rgba(56, 189, 248, 0.2)", borderRadius: "8px", fontSize: "12px", color: "#94a3b8" }}>
            💡 Telegram မှ <code>/ai_status</code> ရိုက်ပို့၍ သို့မဟုတ် <code>[🔄 Refresh Usage]</code> နှိပ်၍ အချိန်မရွေး live usage စစ်ဆေးနိုင်ပါသည်။
          </div>
        </section>
      </div>
    </AppShell>
  );
}

