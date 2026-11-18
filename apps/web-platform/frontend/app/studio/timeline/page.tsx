"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../../components/app-shell";
import { api } from "../../../lib/api";
import {
  Workflow,
  Film,
  Music,
  Volume2,
  Mic,
  Captions,
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  Layers,
  Scissors,
  CheckCircle2,
  ShieldCheck,
  Smartphone,
  Sliders,
} from "lucide-react";

interface TimelineTrackClip {
  id: string;
  name: string;
  start: number;
  duration: number;
  color: string;
}

export default function TimelineStudioPage() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [playheadTime, setPlayheadTime] = useState(0.0);
  const totalDuration = 60.0;

  // Multi-tracks
  const [videoTrack, setVideoTrack] = useState<TimelineTrackClip[]>([
    { id: "v1", name: "Scene 1: Alley Wide Establishing", start: 0.0, duration: 4.5, color: "#0284c7" },
    { id: "v2", name: "Scene 2: Detective Eye Close-Up", start: 4.5, duration: 5.0, color: "#0369a1" },
    { id: "v3", name: "Scene 3: Low Angle Hero Stance", start: 9.5, duration: 6.0, color: "#0284c7" },
    { id: "v4", name: "Scene 4: Cyber Glitch Reveal", start: 15.5, duration: 4.5, color: "#0369a1" },
    { id: "v5", name: "Scene 5: Rain Drone Panorama", start: 20.0, duration: 10.0, color: "#0284c7" },
  ]);

  const [brollTrack, setBrollTrack] = useState<TimelineTrackClip[]>([
    { id: "b1", name: "Neon Sign Flicker Overlay", start: 2.0, duration: 2.5, color: "#059669" },
    { id: "b2", name: "Raindrops on Pavement Macro", start: 12.0, duration: 3.5, color: "#059669" },
  ]);

  const [voiceTrack, setVoiceTrack] = useState<TimelineTrackClip[]>([
    { id: "vo1", name: "မြန်မာစကားပြောသံစဉ် အပိုင်း ၁ (Hook)", start: 0.5, duration: 8.0, color: "#d97706" },
    { id: "vo2", name: "မြန်မာစကားပြောသံစဉ် အပိုင်း ၂ (Conflict)", start: 10.0, duration: 12.0, color: "#d97706" },
  ]);

  const [bgmTrack, setBgmTrack] = useState<TimelineTrackClip[]>([
    { id: "bgm1", name: "Wrath of the Ancient Realm (Two Steps From Hell)", start: 0.0, duration: 30.0, color: "#7c3aed" },
  ]);

  const [sfxTrack, setSfxTrack] = useState<TimelineTrackClip[]>([
    { id: "sfx1", name: "Titan Sub-Bass Slam", start: 0.2, duration: 2.5, color: "#e11d48" },
    { id: "sfx2", name: "Neon Whip Transition", start: 4.4, duration: 1.2, color: "#e11d48" },
    { id: "sfx3", name: "Tension Riser Buildup", start: 8.5, duration: 5.0, color: "#e11d48" },
  ]);

  const [subtitleTrack, setSubtitleTrack] = useState<TimelineTrackClip[]>([
    { id: "sub1", name: "ရန်ကုန်မြို့ကြီးရဲ့ အမှောင်ထုထဲမှာ...", start: 0.5, duration: 4.0, color: "#0891b2" },
    { id: "sub2", name: "ဘယ်သူမှ မသိသေးတဲ့ လျှို့ဝှက်ချက်တစ်ခု...", start: 4.5, duration: 4.0, color: "#0891b2" },
    { id: "sub3", name: "စတင်နိုးထလာခဲ့ပြီဖြစ်ပါတယ်။", start: 8.5, duration: 4.0, color: "#0891b2" },
  ]);

  useEffect(() => {
    let timer: any;
    if (isPlaying) {
      timer = setInterval(() => {
        setPlayheadTime((prev) => (prev >= totalDuration ? 0 : prev + 0.5));
      }, 500);
    }
    return () => clearInterval(timer);
  }, [isPlaying]);

  const renderTrackRow = (label: string, icon: any, clips: TimelineTrackClip[], trackHeight = 36) => {
    const Icon = icon;
    return (
      <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: "8px", alignItems: "center" }}>
        <div style={{
          fontSize: "12px",
          fontWeight: 600,
          color: "#94a3b8",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          paddingLeft: "8px",
        }}>
          <Icon size={14} color="#64748b" />
          <span>{label}</span>
        </div>

        <div style={{
          height: `${trackHeight}px`,
          background: "#080d1a",
          border: "1px solid #1e293b",
          borderRadius: "6px",
          position: "relative",
          overflow: "hidden",
        }}>
          {clips.map((clip) => {
            const leftPct = (clip.start / totalDuration) * 100;
            const widthPct = (clip.duration / totalDuration) * 100;
            return (
              <div
                key={clip.id}
                style={{
                  position: "absolute",
                  left: `${leftPct}%`,
                  width: `${widthPct}%`,
                  height: "100%",
                  background: clip.color,
                  borderRadius: "4px",
                  border: "1px solid rgba(255, 255, 255, 0.2)",
                  padding: "0 8px",
                  display: "flex",
                  alignItems: "center",
                  fontSize: "11px",
                  fontWeight: 600,
                  color: "#ffffff",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  cursor: "grab",
                  boxShadow: "0 2px 4px rgba(0, 0, 0, 0.3)",
                }}
              >
                {clip.name}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <AppShell title="Multi-Track Timeline Studio">
      <div style={{ display: "flex", flexDirection: "column", gap: "20px", paddingBottom: "48px" }}>
        
        {/* Top Playback & Format Bar */}
        <div style={{
          background: "#0b1220",
          border: "1px solid #1e293b",
          borderRadius: "14px",
          padding: "16px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            <button
              type="button"
              onClick={() => setIsPlaying(!isPlaying)}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                background: isPlaying ? "#ef4444" : "#10b981",
                border: "none",
                color: "#ffffff",
                cursor: "pointer",
              }}
            >
              {isPlaying ? <Pause size={18} /> : <Play size={18} style={{ marginLeft: "2px" }} />}
            </button>

            <button
              type="button"
              onClick={() => setPlayheadTime(0.0)}
              style={{
                background: "transparent",
                border: "1px solid #1e293b",
                borderRadius: "8px",
                padding: "8px",
                color: "#94a3b8",
                cursor: "pointer",
              }}
            >
              <RotateCcw size={16} />
            </button>

            <div style={{ fontSize: "18px", fontWeight: 700, fontFamily: "monospace", color: "#38bdf8" }}>
              {Math.floor(playheadTime / 60).toString().padStart(2, "0")}:
              {Math.floor(playheadTime % 60).toString().padStart(2, "0")}.
              {Math.floor((playheadTime % 1) * 10)}
              <span style={{ fontSize: "13px", color: "#64748b" }}> / 01:00.0</span>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{
              display: "flex",
              alignItems: "center",
              gap: "4px",
              padding: "5px 12px",
              background: "rgba(56, 189, 248, 0.15)",
              border: "1px solid rgba(56, 189, 248, 0.3)",
              borderRadius: "20px",
              fontSize: "12px",
              fontWeight: 600,
              color: "#38bdf8",
            }}>
              <Smartphone size={13} /> 9:16 Vertical Export Profile
            </span>
          </div>
        </div>

        {/* Studio Center Stage: Left Video Preview + Right Properties */}
        <div style={{ display: "grid", gridTemplateColumns: "360px 1fr", gap: "20px" }}>
          
          {/* Vertical Video Monitor 9:16 */}
          <div style={{
            background: "#080d1a",
            border: "1px solid #1e293b",
            borderRadius: "14px",
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}>
            <div style={{
              width: "216px",
              height: "384px",
              background: "linear-gradient(180deg, #0b1220, #020617)",
              border: "2px solid rgba(56, 189, 248, 0.4)",
              borderRadius: "16px",
              position: "relative",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              padding: "16px",
              boxShadow: "0 10px 25px rgba(0,0,0,0.6)",
            }}>
              <div style={{ fontSize: "10px", color: "#38bdf8", fontWeight: 700, letterSpacing: "0.05em" }}>
                9:16 PREVIEW MONITOR
              </div>

              {/* Dynamic Center Simulation */}
              <div style={{ textAlign: "center", color: "#f8fafc" }}>
                <Film size={28} color="#38bdf8" style={{ margin: "0 auto 8px auto" }} />
                <div style={{ fontSize: "13px", fontWeight: 600 }}>Alleyway Neo-Noir</div>
                <div style={{ fontSize: "11px", color: "#64748b" }}>Speed: 1.0x (Normal)</div>
              </div>

              {/* Live Burmese Subtitle Overlay */}
              <div style={{
                background: "rgba(0, 0, 0, 0.75)",
                padding: "8px",
                borderRadius: "6px",
                textAlign: "center",
                fontSize: "12.5px",
                fontWeight: 700,
                color: "#facc15",
                textShadow: "0 2px 4px rgba(0,0,0,0.9)",
              }}>
                ရန်ကုန်မြို့ကြီးရဲ့ အမှောင်ထုထဲမှာ...
              </div>
            </div>
          </div>

          {/* Right Info: Track Details & Snap-to-Beat */}
          <div style={{
            background: "#0b1220",
            border: "1px solid #1e293b",
            borderRadius: "14px",
            padding: "24px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}>
            <div>
              <div style={{ fontSize: "12px", fontWeight: 700, color: "#10b981", textTransform: "uppercase", marginBottom: "6px" }}>
                Active Smart Editing Engine
              </div>
              <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#f8fafc", margin: "0 0 10px 0" }}>
                Beat-Synchronized Clip Alignment
              </h3>
              <p style={{ fontSize: "13.5px", color: "#94a3b8", lineHeight: "1.6", margin: "0 0 16px 0" }}>
                AI Creative Director မှ ရွေးချယ်ထားသော အကောင်းဆုံး B-Roll Highlight များကို Background Music ၏
                Beat Drop (14.2s, 42.0s) အမှတ်များနှင့် အလိုအလျောက် ချိန်ညှိပြီး Multi-track အဖြစ် စီစဉ်ပေးထားပါသည်။
              </p>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px", background: "#080d1a", padding: "14px", borderRadius: "10px" }}>
                <div>
                  <div style={{ fontSize: "11px", color: "#64748b" }}>Cut Points</div>
                  <div style={{ fontSize: "16px", fontWeight: 700, color: "#38bdf8" }}>5 Clips</div>
                </div>
                <div>
                  <div style={{ fontSize: "11px", color: "#64748b" }}>Audio Ducking</div>
                  <div style={{ fontSize: "16px", fontWeight: 700, color: "#10b981" }}>-14 dB Active</div>
                </div>
                <div>
                  <div style={{ fontSize: "11px", color: "#64748b" }}>Transitions</div>
                  <div style={{ fontSize: "16px", fontWeight: 700, color: "#f59e0b" }}>3 Whooshes</div>
                </div>
              </div>
            </div>

            <div style={{ display: "flex", gap: "12px", marginTop: "24px" }}>
              <button
                type="button"
                style={{
                  flex: 1,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  padding: "12px",
                  background: "linear-gradient(135deg, #0284c7, #0369a1)",
                  border: "none",
                  borderRadius: "8px",
                  color: "#ffffff",
                  fontSize: "14px",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                <CheckCircle2 size={16} />
                Save Multi-Track Timeline
              </button>
            </div>
          </div>

        </div>

        {/* Bottom Multi-Track Visual Timeline */}
        <div style={{
          background: "#0b1220",
          border: "1px solid #1e293b",
          borderRadius: "14px",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          position: "relative",
        }}>
          {/* Timeline Time Ruler */}
          <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: "8px", borderBottom: "1px solid #1e293b", paddingBottom: "6px" }}>
            <span style={{ fontSize: "11px", color: "#64748b", fontWeight: 700 }}>TRACKS</span>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "10.5px", color: "#64748b", padding: "0 4px" }}>
              <span>00:00</span>
              <span>00:15</span>
              <span>00:30</span>
              <span>00:45</span>
              <span>01:00</span>
            </div>
          </div>

          {/* Tracks */}
          {renderTrackRow("Video Primary (A-Roll)", Film, videoTrack)}
          {renderTrackRow("Overlay B-Roll", Layers, brollTrack, 30)}
          {renderTrackRow("Voice Narration", Mic, voiceTrack, 30)}
          {renderTrackRow("Epic BGM Score", Music, bgmTrack, 30)}
          {renderTrackRow("Cinematic SFX", Volume2, sfxTrack, 26)}
          {renderTrackRow("Burmese Subtitles", Captions, subtitleTrack, 26)}
        </div>

      </div>
    </AppShell>
  );
}
