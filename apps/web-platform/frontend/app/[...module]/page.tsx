"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { AppShell } from "../../components/app-shell";
import { api, Episode } from "../../lib/api";

const studioMappings: Record<string, { title: string; subpath: string; icon: string; desc: string }> = {
  "script-studio": { title: "Script Studio", subpath: "script", icon: "📝", desc: "Write, generate with Gemini/Groq, and edit Burmese video scripts." },
  "scene-breakdown": { title: "Scene Breakdown Studio", subpath: "scenes", icon: "🎬", desc: "Visual prompts, B-roll timing, and audio cues per scene." },
  "assets": { title: "Asset Library", subpath: "assets", icon: "📁", desc: "Audio voiceovers, video cuts, and media attachments for episodes." },
  "subtitles": { title: "Subtitle Studio", subpath: "subtitle", icon: "💬", desc: "AI Speech-to-Text transcription with Groq Whisper & Cloudflare." },
  "review": { title: "Review Center", subpath: "review", icon: "🔍", desc: "Editorial approval, QA checklist, and final render sign-off." },
  "export": { title: "Drive Export", subpath: "export", icon: "🚀", desc: "Package and export finished assets directly to Google Drive." },
};

export default function ModulePage({ params }: { params: Promise<{ module: string[] }> }) {
  const resolvedParams = use(params);
  const rawKey = resolvedParams.module.join("/");
  const studio = studioMappings[rawKey] || studioMappings[resolvedParams.module[0]];

  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listEpisodes()
      .then(setEpisodes)
      .catch(() => setEpisodes([]))
      .finally(() => setLoading(false));
  }, []);

  const pageTitle = studio ? studio.title : resolvedParams.module.map(x => x.replace(/-/g, " ")).join(" / ").replace(/\b\w/g, c => c.toUpperCase());

  return (
    <AppShell title={pageTitle}>
      <div className="ds-stack" style={{ gap: "24px" }}>
        {studio ? (
          <>
            <div className="ds-card" style={{ padding: "26px", border: "1px solid var(--border)", background: "linear-gradient(135deg, rgba(15, 22, 38, 0.95), rgba(22, 32, 52, 0.6))" }}>
              <div style={{ display: "flex", gap: "16px", alignItems: "flex-start" }}>
                <span style={{ fontSize: "32px", lineHeight: 1 }}>{studio.icon}</span>
                <div>
                  <div className="eyebrow">PRODUCTION LAUNCHER</div>
                  <h2 style={{ fontSize: "22px", fontWeight: 700, marginTop: "4px", color: "#f8fafc" }}>
                    {studio.title}
                  </h2>
                  <p style={{ fontSize: "14px", color: "#94a3b8", marginTop: "6px" }}>
                    {studio.desc}
                  </p>
                </div>
              </div>
            </div>

            <div className="ds-card" style={{ padding: "24px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                <div>
                  <div className="eyebrow">EPISODE SELECTION</div>
                  <h3 style={{ fontSize: "16px", fontWeight: 600, color: "#f8fafc", marginTop: "4px" }}>
                    Select an episode to launch {studio.title}
                  </h3>
                </div>
                <Link href="/episodes" className="ds-button" style={{ padding: "6px 14px", fontSize: "12px", textDecoration: "none" }}>
                  + Create New Episode
                </Link>
              </div>

              {loading ? (
                <div style={{ padding: "30px", textAlign: "center", color: "#94a3b8", fontSize: "14px" }}>
                  Loading studio episodes…
                </div>
              ) : episodes.length === 0 ? (
                <div style={{ padding: "40px 20px", textAlign: "center", border: "1px dashed #1e293b", borderRadius: "12px" }}>
                  <div style={{ fontSize: "28px", marginBottom: "8px" }}>🎬</div>
                  <h4 style={{ fontSize: "15px", fontWeight: 600, color: "#f8fafc" }}>No Episodes Created Yet</h4>
                  <p style={{ fontSize: "13px", color: "#64748b", marginTop: "4px", maxWidth: "340px", margin: "4px auto 16px" }}>
                    To use {studio.title}, first create an episode or generate a batch from the Episodes manager.
                  </p>
                  <Link href="/episodes" className="ds-button primary" style={{ padding: "8px 18px", fontSize: "13px", textDecoration: "none" }}>
                    Go to Episodes Manager
                  </Link>
                </div>
              ) : (
                <div style={{ display: "grid", gap: "10px" }}>
                  {episodes.map((ep) => (
                    <div
                      key={ep.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "14px 18px",
                        backgroundColor: "#0b1424",
                        border: "1px solid #1e293b",
                        borderRadius: "12px",
                        gap: "16px",
                      }}
                    >
                      <div style={{ minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <span style={{ fontSize: "11px", fontWeight: 700, padding: "2px 8px", borderRadius: "6px", backgroundColor: "#1e293b", color: "#38bdf8" }}>
                            EP {ep.episode_number}
                          </span>
                          <span style={{ fontSize: "14px", fontWeight: 600, color: "#f8fafc" }}>
                            {ep.title}
                          </span>
                        </div>
                        <div style={{ fontSize: "12px", color: "#64748b", marginTop: "4px" }}>
                          Status: <span style={{ color: "#94a3b8", textTransform: "capitalize" }}>{ep.status}</span> · Duration: {ep.target_duration_seconds}s
                        </div>
                      </div>

                      <Link
                        href={`/episodes/${ep.id}/${studio.subpath}`}
                        className="ds-button primary"
                        style={{
                          padding: "8px 18px",
                          fontSize: "12px",
                          fontWeight: 600,
                          textDecoration: "none",
                          whiteSpace: "nowrap",
                        }}
                      >
                        Open Studio &rarr;
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        ) : (
          <section className="ds-card" style={{ padding: "24px" }}>
            <div className="eyebrow">STUDIO MODULE</div>
            <h2 style={{ fontSize: "20px", fontWeight: 700, marginTop: "6px", color: "#f8fafc" }}>{pageTitle}</h2>
            <p style={{ fontSize: "14px", color: "#94a3b8", marginTop: "8px" }}>
              Active studio module in Narrativ-Forge production workspace.
            </p>
          </section>
        )}
      </div>
    </AppShell>
  );
}