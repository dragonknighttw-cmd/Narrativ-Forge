"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../../components/app-shell";
import { api } from "../../../lib/api";
import {
  Music,
  Volume2,
  Sliders,
  Play,
  Pause,
  Sparkles,
  Zap,
  Flame,
  Radio,
  CheckCircle2,
  Layers,
  ArrowRight,
} from "lucide-react";

interface MusicTrack {
  id: string;
  title: string;
  genre: string;
  mood: string;
  bpm: number;
  duration_seconds: number;
  file_url: string;
  beat_drops: number[];
  license_type: string;
}

interface SfxTrack {
  id: string;
  title: string;
  category: string;
  duration_seconds: number;
  file_url: string;
  ducking_db: number;
}

const SAMPLE_MUSIC: MusicTrack[] = [
  {
    id: "m1",
    title: "Wrath of the Ancient Realm (Two Steps From Hell Tribute)",
    genre: "epic_orchestral",
    mood: "Heroic, Powerful, War Drums",
    bpm: 138,
    duration_seconds: 185.0,
    file_url: "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=epic-cinematic-trailer-113981.mp3",
    beat_drops: [14.2, 42.0, 84.5, 126.0],
    license_type: "Royalty-Free / Studio Safe",
  },
  {
    id: "m2",
    title: "Midnight Cyber Drift (Aggressive Phonk)",
    genre: "phonk_electronic",
    mood: "Dark, Hyped, Bass Heavy",
    bpm: 142,
    duration_seconds: 130.0,
    file_url: "https://cdn.pixabay.com/download/audio/2023/06/13/audio_73e72844a4.mp3?filename=dark-ambient-techno-151475.mp3",
    beat_drops: [8.0, 32.0, 64.0, 96.0],
    license_type: "Royalty-Free / Studio Safe",
  },
  {
    id: "m3",
    title: "Elegy for Fallen Shadows (Piano & Cello Solo)",
    genre: "emotional_dramatic",
    mood: "Sad, Moving, Nostalgic",
    bpm: 86,
    duration_seconds: 210.0,
    file_url: "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8bbf73467.mp3?filename=cinematic-piano-10786.mp3",
    beat_drops: [28.0, 68.0, 140.0],
    license_type: "Royalty-Free / Studio Safe",
  },
];

const SAMPLE_SFX: SfxTrack[] = [
  { id: "s1", title: "Titan Sub-Bass Cinematic Slam", category: "cinematic_impact", duration_seconds: 2.8, file_url: "/sfx/impact.mp3", ducking_db: -16.0 },
  { id: "s2", title: "Hyper-Fast Neon Whip Transition", category: "whoosh_transition", duration_seconds: 1.2, file_url: "/sfx/whoosh.mp3", ducking_db: -12.0 },
  { id: "s3", title: "Shepard Tone Dread Tension Riser", category: "riser_buildup", duration_seconds: 6.5, file_url: "/sfx/riser.mp3", ducking_db: -10.0 },
  { id: "s4", title: "Cyberpunk Rain & Distant Siren Room Tone", category: "ambient_drone", duration_seconds: 30.0, file_url: "/sfx/rain.mp3", ducking_db: -18.0 },
];

export default function MusicStudioPage() {
  const [musicList, setMusicList] = useState<MusicTrack[]>(SAMPLE_MUSIC);
  const [sfxList, setSfxList] = useState<SfxTrack[]>(SAMPLE_SFX);
  const [activeTrack, setActiveTrack] = useState<MusicTrack>(SAMPLE_MUSIC[0]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duckingLevel, setDuckingLevel] = useState("-14");

  useEffect(() => {
    async function load() {
      try {
        const m = await api.getMusicCatalog();
        if (m && m.length > 0) {
          setMusicList(m);
          setActiveTrack(m[0]);
        }
        const s = await api.getSfxCatalog();
        if (s && s.length > 0) setSfxList(s);
      } catch {
        // Fallback smooth preview
      }
    }
    load();
  }, []);

  return (
    <AppShell title="AI Music & Cinematic Sound Design Engine">
      <div style={{ display: "flex", flexDirection: "column", gap: "24px", paddingBottom: "48px" }}>
        
        {/* Intro */}
        <div style={{
          background: "#0b1220",
          border: "1px solid #1e293b",
          borderRadius: "14px",
          padding: "24px",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#a855f7", fontSize: "12px", fontWeight: 700, letterSpacing: "0.05em", marginBottom: "6px" }}>
            <Music size={14} /> MODULE 05 & 06 · MUSIC & SOUND DESIGN
          </div>
          <h2 style={{ fontSize: "22px", fontWeight: 700, color: "#f8fafc", margin: "0 0 6px 0" }}>
            Cinematic Orchestral Scoring & Beat Drop Synchronization
          </h2>
          <p style={{ fontSize: "14px", color: "#94a3b8", margin: 0, maxWidth: "750px", lineHeight: "1.5" }}>
            Two Steps From Hell ကဲ့သို့ အားကောင်းသော Epic Orchestral War Drums နှင့် Bass-Heavy Phonk အသံများကို
            ရုပ်သံလှုပ်ရှားမှုနှင့် ကွက်တိကျစေမည့် Beat Drop Grid စနစ်ဖြင့် ပေါင်းစပ်ပေးပါသည်။
            Visual Transition များတွင် Impact, Whoosh, Riser SFX များကို -14dB Audio Ducking ဖြင့် အလိုအလျောက် ချိန်ညှိပေးပါသည်။
          </p>
        </div>

        {/* 2-Column Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "24px" }}>
          
          {/* Left: Music Scores */}
          <div style={{
            background: "#0b1220",
            border: "1px solid #1e293b",
            borderRadius: "14px",
            padding: "24px",
          }}>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "#f1f5f9", margin: "0 0 16px 0", display: "flex", alignItems: "center", gap: "8px" }}>
              <Music size={16} color="#a855f7" /> Epic Soundtracks & Score Catalog
            </h3>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {musicList.map((m) => {
                const isSelected = activeTrack?.id === m.id;
                return (
                  <div
                    key={m.id}
                    onClick={() => setActiveTrack(m)}
                    style={{
                      padding: "16px",
                      borderRadius: "10px",
                      background: isSelected ? "rgba(168, 85, 247, 0.08)" : "#080d1a",
                      border: `1.5px solid ${isSelected ? "#a855f7" : "#1e293b"}`,
                      cursor: "pointer",
                      display: "flex",
                      flexDirection: "column",
                      gap: "10px",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                      <div>
                        <div style={{ fontSize: "14.5px", fontWeight: 600, color: "#f8fafc" }}>{m.title}</div>
                        <div style={{ fontSize: "12px", color: "#64748b", marginTop: "2px" }}>
                          {m.mood} • {m.bpm} BPM • {m.duration_seconds}s
                        </div>
                      </div>
                      <span style={{
                        fontSize: "11px",
                        fontWeight: 600,
                        padding: "2px 8px",
                        borderRadius: "4px",
                        background: "rgba(168, 85, 247, 0.15)",
                        color: "#c084fc",
                      }}>
                        {m.genre.replace(/_/g, " ")}
                      </span>
                    </div>

                    {/* Beat Grid Display */}
                    <div style={{ background: "rgba(0,0,0,0.3)", padding: "8px 12px", borderRadius: "6px" }}>
                      <div style={{ fontSize: "11px", color: "#64748b", marginBottom: "4px" }}>
                        Beat Drop Synchronization Points (Seconds):
                      </div>
                      <div style={{ display: "flex", gap: "8px" }}>
                        {m.beat_drops.map((drop, i) => (
                          <span key={i} style={{
                            fontSize: "11px",
                            fontWeight: 700,
                            padding: "2px 6px",
                            background: "rgba(56, 189, 248, 0.15)",
                            borderRadius: "4px",
                            color: "#38bdf8",
                          }}>
                            {drop}s
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right: Sound Design SFX & Audio Ducking Settings */}
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            
            {/* SFX Catalog */}
            <div style={{
              background: "#0b1220",
              border: "1px solid #1e293b",
              borderRadius: "14px",
              padding: "24px",
            }}>
              <h3 style={{ fontSize: "16px", fontWeight: 600, color: "#f1f5f9", margin: "0 0 16px 0", display: "flex", alignItems: "center", gap: "8px" }}>
                <Volume2 size={16} color="#38bdf8" /> Cinematic Sound Design Layers
              </h3>

              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {sfxList.map((s) => (
                  <div
                    key={s.id}
                    style={{
                      padding: "12px 14px",
                      background: "#080d1a",
                      border: "1px solid #1e293b",
                      borderRadius: "8px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <div style={{ fontSize: "13.5px", fontWeight: 600, color: "#f8fafc" }}>{s.title}</div>
                      <div style={{ fontSize: "11px", color: "#64748b", marginTop: "2px" }}>
                        {s.category.replace(/_/g, " ")} • {s.duration_seconds}s
                      </div>
                    </div>
                    <span style={{ fontSize: "11px", color: "#10b981", fontWeight: 600 }}>
                      Auto-Ducking: {s.ducking_db}dB
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Audio Ducking & Balancing Controller */}
            <div style={{
              background: "#0b1220",
              border: "1px solid #1e293b",
              borderRadius: "14px",
              padding: "24px",
            }}>
              <h3 style={{ fontSize: "15px", fontWeight: 600, color: "#f1f5f9", margin: "0 0 12px 0", display: "flex", alignItems: "center", gap: "8px" }}>
                <Sliders size={15} color="#10b981" /> Voice & Music Balancing (Auto-Ducking)
              </h3>
              <p style={{ fontSize: "12.5px", color: "#94a3b8", lineHeight: "1.5", margin: "0 0 16px 0" }}>
                မြန်မာစကားပြောသံစဉ် စကားစတင်ပြောချိန်တွင် Background Score ကို အလိုအလျောက် လျှော့ချပေးမည့် Profile ဖြစ်ပါသည်။
              </p>

              <div>
                <label style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px", color: "#f1f5f9", fontWeight: 600, marginBottom: "8px" }}>
                  <span>Ducking Attenuation Level</span>
                  <span style={{ color: "#38bdf8" }}>{duckingLevel} dB</span>
                </label>
                <input
                  type="range"
                  min="-24"
                  max="-6"
                  value={duckingLevel}
                  onChange={(e) => setDuckingLevel(e.target.value)}
                  style={{ width: "100%", accentColor: "#38bdf8" }}
                />
              </div>

              <button
                type="button"
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  padding: "11px",
                  background: "linear-gradient(135deg, #9333ea, #7e22ce)",
                  border: "none",
                  borderRadius: "8px",
                  color: "#ffffff",
                  fontSize: "13.5px",
                  fontWeight: 600,
                  cursor: "pointer",
                  marginTop: "20px",
                }}
              >
                <CheckCircle2 size={15} />
                Sync Soundscape to Multi-Track Timeline
              </button>
            </div>

          </div>

        </div>

      </div>
    </AppShell>
  );
}
