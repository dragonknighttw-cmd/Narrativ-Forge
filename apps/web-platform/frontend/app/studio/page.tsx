"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  Sparkles,
  Film,
  FolderOpen,
  Clapperboard,
  SlidersHorizontal,
  Workflow,
  ClipboardCheck,
  ArrowRight,
  Zap,
  Activity,
  CheckCircle2,
  Layers,
  Music,
  Volume2,
  ShieldCheck,
  Scissors,
} from "lucide-react";
import { AppShell } from "../../components/app-shell";
import { api } from "../../lib/api";

const MODULES = [
  {
    num: "01",
    title: "Reference Intelligence",
    href: "/studio/reference",
    icon: Film,
    desc: "Upload reference videos to extract camera movement, shot duration, color grade, and storytelling structures.",
    badge: "Vision Engine",
    color: "from-cyan-500/20 to-blue-500/10 border-cyan-500/30 text-cyan-400",
  },
  {
    num: "02",
    title: "Raw Footage Hub",
    href: "/studio/footage",
    icon: FolderOpen,
    desc: "AI scans raw video files, detects sub-scenes, scores frame stability, detects blur, and flags best highlight B-roll.",
    badge: "Automated Detection",
    color: "from-emerald-500/20 to-teal-500/10 border-emerald-500/30 text-emerald-400",
  },
  {
    num: "03",
    title: "AI Creative Director",
    href: "/studio/director",
    icon: Clapperboard,
    desc: "Synthesizes 3 distinct editing directions: Epic Cinematic, 9:16 Viral Social, and Emotional Narrative with shot decisions.",
    badge: "Decision Engine",
    color: "from-amber-500/20 to-orange-500/10 border-amber-500/30 text-amber-400",
  },
  {
    num: "04",
    title: "Music & Score Engine",
    href: "/studio/music",
    icon: Music,
    desc: "Two Steps From Hell style Epic Orchestral, Phonk, and Battle themes with beat drop grids and -14dB audio ducking.",
    badge: "Audio Intelligence",
    color: "from-purple-500/20 to-indigo-500/10 border-purple-500/30 text-purple-400",
  },
  {
    num: "05",
    title: "Multi-Track Timeline",
    href: "/studio/timeline",
    icon: Workflow,
    desc: "Full multi-track editing workspace: Video, B-roll, Voice, Music, SFX, and Karaoke Burmese Subtitles.",
    badge: "Timeline Studio",
    color: "from-blue-500/20 to-violet-500/10 border-blue-500/30 text-blue-400",
  },
  {
    num: "06",
    title: "Quality Control (QC)",
    href: "/studio/qc",
    icon: ShieldCheck,
    desc: "Pre-export validation for black frames, audio clipping, A/V drift, and subtitle alignment before final rendering.",
    badge: "Export Gate",
    color: "from-rose-500/20 to-pink-500/10 border-rose-500/30 text-rose-400",
  },
];

export default function StudioHubPage() {
  const [stats, setStats] = useState<any>({
    reference_videos: 8,
    raw_footages: 24,
    creative_concepts: 3,
    timeline_projects: 4,
    curated_music_tracks: 4,
    curated_sfx_tracks: 4,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await api.studioOverview();
        if (res?.counts) setStats(res.counts);
      } catch {
        // Fallback smooth studio preview
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  return (
    <AppShell title="AI Creative Production Studio">
      <div style={{ display: "flex", flexDirection: "column", gap: "28px", paddingBottom: "48px" }}>
        
        {/* Hero Banner */}
        <div style={{
          background: "linear-gradient(135deg, rgba(8, 13, 24, 0.95), rgba(15, 23, 42, 0.9))",
          border: "1px solid rgba(56, 189, 248, 0.2)",
          borderRadius: "16px",
          padding: "32px",
          position: "relative",
          overflow: "hidden",
          boxShadow: "0 10px 30px -10px rgba(0, 0, 0, 0.5)",
        }}>
          <div style={{
            position: "absolute",
            top: "-40px",
            right: "-40px",
            width: "220px",
            height: "220px",
            background: "radial-gradient(circle, rgba(6, 182, 212, 0.15), transparent 70%)",
            borderRadius: "50%",
            pointerEvents: "none",
          }} />

          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
            <span style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              padding: "4px 12px",
              background: "rgba(6, 182, 212, 0.15)",
              border: "1px solid rgba(6, 182, 212, 0.3)",
              borderRadius: "20px",
              fontSize: "12px",
              fontWeight: 600,
              color: "#38bdf8",
              letterSpacing: "0.05em",
            }}>
              <Sparkles size={13} />
              AI CREATIVE PRODUCTION EXPANSION
            </span>
            <span style={{ fontSize: "12px", color: "#64748b" }}>• Standalone Studio</span>
          </div>

          <h1 style={{ fontSize: "28px", fontWeight: 700, color: "#f8fafc", margin: "0 0 10px 0" }}>
            Intelligent Video Editing · Cinematic Music · Creative Direction
          </h1>
          <p style={{ fontSize: "15px", color: "#94a3b8", maxWidth: "750px", lineHeight: "1.6", margin: 0 }}>
            AI က Raw Footage တွေကို နားလည်ပြီး အကောင်းဆုံး အစိတ်အပိုင်းတွေကို ရွေးချယ်ပေးမယ်။
            Reference Video တွေဆီက Cinematic Style တွေကို ထုတ်ယူပြီး Two Steps From Hell လို Epic Orchestral Music၊
            Transition SFX တွေနဲ့ ပေါင်းစပ်ကာ Professional 9:16 ဗီဒီယိုအဖြစ် အလိုအလျောက် တည်းဖြတ်ပေးမည့် Creative Studio ဖြစ်ပါတယ်။
          </p>

          {/* Quick Metrics Bar */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
            gap: "16px",
            marginTop: "24px",
            paddingTop: "20px",
            borderTop: "1px solid rgba(255, 255, 255, 0.08)",
          }}>
            <div>
              <div style={{ fontSize: "11px", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>Reference Profiles</div>
              <div style={{ fontSize: "22px", fontWeight: 700, color: "#38bdf8", marginTop: "2px" }}>{stats.reference_videos}</div>
            </div>
            <div>
              <div style={{ fontSize: "11px", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>Raw Footages</div>
              <div style={{ fontSize: "22px", fontWeight: 700, color: "#10b981", marginTop: "2px" }}>{stats.raw_footages}</div>
            </div>
            <div>
              <div style={{ fontSize: "11px", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>Director Concepts</div>
              <div style={{ fontSize: "22px", fontWeight: 700, color: "#f59e0b", marginTop: "2px" }}>{stats.creative_concepts}</div>
            </div>
            <div>
              <div style={{ fontSize: "11px", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>Music & SFX</div>
              <div style={{ fontSize: "22px", fontWeight: 700, color: "#a855f7", marginTop: "2px" }}>{stats.curated_music_tracks + stats.curated_sfx_tracks}</div>
            </div>
            <div>
              <div style={{ fontSize: "11px", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>Timelines Ready</div>
              <div style={{ fontSize: "22px", fontWeight: 700, color: "#60a5fa", marginTop: "2px" }}>{stats.timeline_projects}</div>
            </div>
          </div>
        </div>

        {/* 6 Studio Module Cards Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
          {MODULES.map((m) => {
            const Icon = m.icon;
            return (
              <Link
                key={m.num}
                href={m.href}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  background: "#0b1220",
                  border: "1px solid #1e293b",
                  borderRadius: "14px",
                  padding: "24px",
                  textDecoration: "none",
                  transition: "all 0.2s ease-in-out",
                  position: "relative",
                  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.2)",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = "rgba(56, 189, 248, 0.4)";
                  e.currentTarget.style.transform = "translateY(-3px)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "#1e293b";
                  e.currentTarget.style.transform = "translateY(0)";
                }}
              >
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                    <div style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      width: "42px",
                      height: "42px",
                      borderRadius: "10px",
                      background: "rgba(15, 23, 42, 0.8)",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      color: "#38bdf8",
                    }}>
                      <Icon size={20} />
                    </div>
                    <span style={{
                      fontSize: "11px",
                      fontWeight: 600,
                      padding: "3px 8px",
                      borderRadius: "6px",
                      background: "rgba(255, 255, 255, 0.05)",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      color: "#94a3b8",
                      letterSpacing: "0.03em",
                    }}>
                      {m.badge}
                    </span>
                  </div>

                  <div style={{ fontSize: "11px", fontWeight: 700, color: "#64748b", marginBottom: "4px" }}>MODULE {m.num}</div>
                  <h3 style={{ fontSize: "18px", fontWeight: 600, color: "#f1f5f9", margin: "0 0 8px 0" }}>{m.title}</h3>
                  <p style={{ fontSize: "13.5px", color: "#94a3b8", lineHeight: "1.5", margin: 0 }}>{m.desc}</p>
                </div>

                <div style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  fontSize: "13px",
                  fontWeight: 600,
                  color: "#38bdf8",
                  marginTop: "20px",
                  paddingTop: "14px",
                  borderTop: "1px solid rgba(255, 255, 255, 0.05)",
                }}>
                  Launch Studio <ArrowRight size={14} />
                </div>
              </Link>
            );
          })}
        </div>

      </div>
    </AppShell>
  );
}
