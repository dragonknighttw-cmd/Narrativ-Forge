"use client";

import React, { useState, useEffect, useRef } from "react";
import { AppShell } from "../../components/app-shell";
import { apiBase } from "../../lib/api";

interface VideoClipItem {
  id: string;
  title: string;
  provider: string;
  duration_seconds: number;
  source_url: string;
  transition: string;
}

type LocalRenderJob = { id: string; title: string; createdAt: string; duration: number; status: "planned" | "ready"; command: string };
const RENDER_QUEUE_KEY = "narrativ-local-render-queue-v1";

export default function VideoComposerPage() {
  const [clips, setClips] = useState<VideoClipItem[]>([
    {
      id: "clip_01",
      title: "Kling AI - Neo Bagan Cyberpunk Flight",
      provider: "kling_ai",
      duration_seconds: 6.0,
      source_url: "https://storage.googleapis.com/sample/kling_clip1.mp4",
      transition: "cross_dissolve",
    },
    {
      id: "clip_02",
      title: "Runway Gen-3 - Mech Awakening Close-Up",
      provider: "runway_gen3",
      duration_seconds: 4.5,
      source_url: "https://storage.googleapis.com/sample/runway_clip2.mp4",
      transition: "cut",
    },
    {
      id: "clip_03",
      title: "Luma Dream Machine - Solar Flare Blast",
      provider: "luma_dream_machine",
      duration_seconds: 5.0,
      source_url: "https://storage.googleapis.com/sample/luma_clip3.mp4",
      transition: "anime_flash",
    },
  ]);

  const [newUrl, setNewUrl] = useState("");
  const [newTitle, setNewTitle] = useState("");
  const [newProvider, setNewProvider] = useState("kling_ai");
  const [newDuration, setNewDuration] = useState("5.0");
  const [bgmVolume, setBgmVolume] = useState(25);
  
  // Playback Monitor State
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0.0);
  const [ffmpegCommand, setFfmpegCommand] = useState<string | null>(null);
  const [isCompiled, setIsCompiled] = useState(false);
  const [isCompiling, setIsCompiling] = useState(false);
  const [compileStatus, setCompileStatus] = useState("");
  const [renderJobs, setRenderJobs] = useState<LocalRenderJob[]>([]);
  const queueImportRef = useRef<HTMLInputElement>(null);

  const totalDuration = clips.reduce((acc, c) => acc + c.duration_seconds, 0);

  useEffect(() => {
    try {
      const saved: unknown = JSON.parse(window.localStorage.getItem(RENDER_QUEUE_KEY) || "[]");
      if (Array.isArray(saved)) setRenderJobs(saved.filter((job): job is LocalRenderJob => Boolean(job && typeof job.id === "string" && typeof job.command === "string")));
    } catch { /* a corrupt local queue is ignored rather than blocking editing */ }
  }, []);

  const saveRenderJobs = (next: LocalRenderJob[]) => {
    setRenderJobs(next);
    window.localStorage.setItem(RENDER_QUEUE_KEY, JSON.stringify(next.slice(0, 20)));
  };

  const exportRenderQueue = () => {
    const blob = new Blob([JSON.stringify({ format: "narrativ-local-render-queue", version: 1, jobs: renderJobs }, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob); const anchor = document.createElement("a"); anchor.href = url; anchor.download = "narrativ-render-queue.json"; anchor.click(); URL.revokeObjectURL(url);
  };
  const importRenderQueue = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]; event.target.value = ""; if (!file) return;
    try {
      const value: unknown = JSON.parse(await file.text());
      if (!value || typeof value !== "object" || (value as { format?: string }).format !== "narrativ-local-render-queue" || !Array.isArray((value as { jobs?: unknown[] }).jobs)) throw new Error("Invalid render queue");
      const incoming = (value as { jobs: unknown[] }).jobs.filter((job): job is LocalRenderJob => Boolean(job && typeof (job as LocalRenderJob).id === "string" && typeof (job as LocalRenderJob).command === "string" && typeof (job as LocalRenderJob).title === "string"));
      saveRenderJobs([...renderJobs, ...incoming.filter((job) => !renderJobs.some((existing) => existing.id === job.id))]);
    } catch { window.alert("This file is not a valid Narrativ local render queue."); }
  };

  // Playback timer simulation
  useEffect(() => {
    let interval: any = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime((prev) => {
          if (prev >= totalDuration) {
            setIsPlaying(false);
            return 0.0;
          }
          return Math.round((prev + 0.1) * 10) / 10;
        });
      }, 100);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isPlaying, totalDuration]);

  // Find active clip
  let accumulatedTime = 0;
  let activeClip = clips[0];
  for (const c of clips) {
    if (currentTime >= accumulatedTime && currentTime <= accumulatedTime + c.duration_seconds) {
      activeClip = c;
      break;
    }
    accumulatedTime += c.duration_seconds;
  }

  const handleAddClip = () => {
    if (!newUrl.trim() || !newTitle.trim()) return;
    const item: VideoClipItem = {
      id: `clip_${Date.now()}`,
      title: newTitle,
      provider: newProvider,
      duration_seconds: parseFloat(newDuration) || 5.0,
      source_url: newUrl,
      transition: "cut",
    };
    setClips([...clips, item]);
    setNewUrl("");
    setNewTitle("");
  };

  const handleCompileTimeline = async () => {
    if (isCompiling || clips.length === 0) return;
    setIsCompiling(true);
    setCompileStatus("Building a local render plan…");
    setIsCompiled(true);
    try {
      const res = await fetch(`${apiBase}/video-composer/render-ffmpeg-spec`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: "Anime Battle Episode 1 Final Cut",
          video_clips: clips,
          target_aspect_ratio: "9:16",
        }),
      });
      let command: string;
      if (res.ok) {
        const data = await res.json();
        command = data.ffmpeg_command;
      } else {
        command = `ffmpeg -y -f lavfi -i color=c=black:s=1080x1920:r=30:d=${totalDuration} -c:v libx264 -b:a 192k output_shorts_1080x1920.mp4`;
      }
      setFfmpegCommand(command);
      saveRenderJobs([{ id: crypto.randomUUID(), title: "Anime Battle Episode 1 Final Cut", createdAt: new Date().toISOString(), duration: totalDuration, status: "ready", command }, ...renderJobs]);
      setCompileStatus("Render plan ready. Copy or export the command to render locally.");
    } catch {
      const command = `ffmpeg -y -f lavfi -i color=c=black:s=1080x1920:r=30:d=${totalDuration} -c:v libx264 -b:a 192k output_shorts_1080x1920.mp4`;
      setFfmpegCommand(command);
      saveRenderJobs([{ id: crypto.randomUUID(), title: "Anime Battle Episode 1 Final Cut", createdAt: new Date().toISOString(), duration: totalDuration, status: "planned", command }, ...renderJobs]);
      setCompileStatus("The API was unavailable. A local fallback render plan was saved.");
    } finally {
      setIsCompiling(false);
      setIsCompiled(false);
    }
  };

  return (
    <AppShell title="Multi-Track Video Clip Composer">
      <div className="ds-stack" style={{ gap: "20px" }}>
        {/* Composer Header Banner */}
        <div
          className="ds-card"
          style={{
            padding: "24px",
            background: "linear-gradient(135deg, rgba(20, 83, 45, 0.4), rgba(15, 23, 42, 0.95))",
            border: "1px solid rgba(34, 197, 94, 0.3)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
            <div>
              <div className="eyebrow" style={{ color: "#4ade80" }}>HYBRID VIDEO ASSEMBLY</div>
              <h2 style={{ fontSize: "22px", fontWeight: 700, color: "#f8fafc", marginTop: "4px" }}>
                Multi-Track AI Video Composer
              </h2>
              <p style={{ fontSize: "14px", color: "#94a3b8", marginTop: "6px", maxWidth: "600px" }}>
                Import video clips from Runway, Kling, Sora, or Luma, arrange multi-track timelines with audio dubbing, BGM auto-ducking, and dynamic subtitles.
              </p>
            </div>
            <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
              <div style={{ fontSize: "12px", color: "#94a3b8", backgroundColor: "#0b1424", padding: "6px 12px", borderRadius: "8px", border: "1px solid #1e293b" }}>
                Timeline: <b style={{ color: "#38bdf8" }}>{currentTime.toFixed(1)}s</b> / {totalDuration.toFixed(1)}s
              </div>
              <button
                type="button"
                onClick={handleCompileTimeline}
                disabled={isCompiling || clips.length === 0}
                className="ds-button primary"
                style={{ fontSize: "12px", padding: "8px 16px" }}
              >
                {isCompiling ? "Building render plan…" : isCompiled ? "✅ Compiled Ready!" : "⚡ Compile & Export (FFmpeg)"}
              </button>
            </div>
          </div>
        </div>

        {/* Live Video Monitor Stage */}
        <div className="ds-card" style={{ padding: "20px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "minmax(280px, 340px) 1fr", gap: "20px" }}>
            {/* 9:16 Video Player Screen */}
            <div
              style={{
                height: "380px",
                borderRadius: "12px",
                backgroundColor: "#05070d",
                border: "2px solid #1e293b",
                position: "relative",
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                padding: "16px",
                boxShadow: "0 8px 32px rgba(0,0,0,0.7)",
              }}
            >
              {/* Top Badge */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "10px", fontWeight: 700, padding: "2px 8px", borderRadius: "4px", backgroundColor: "#38bdf8", color: "#000" }}>
                  9:16 SHORTS PREVIEW
                </span>
                <span style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase" }}>
                  {activeClip ? activeClip.provider.replace("_", " ") : "READY"}
                </span>
              </div>

              {/* Center Active Clip Visualizer */}
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: "36px", marginBottom: "8px" }}>
                  {isPlaying ? "🎞️" : "⏸️"}
                </div>
                <div style={{ fontSize: "13px", fontWeight: 700, color: "#f8fafc" }}>
                  {activeClip ? activeClip.title : "Timeline Idle"}
                </div>
                <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
                  Active Transition: <span style={{ color: "#c084fc" }}>{activeClip?.transition || "cut"}</span>
                </div>
              </div>

              {/* Subtitle Overlay */}
              <div style={{ textAlign: "center" }}>
                <div
                  style={{
                    backgroundColor: "rgba(0,0,0,0.75)",
                    backdropFilter: "blur(4px)",
                    color: "#fef08a",
                    padding: "6px 12px",
                    borderRadius: "8px",
                    border: "1px solid rgba(251, 191, 36, 0.4)",
                    fontSize: "12px",
                    fontWeight: 800,
                    letterSpacing: "0.5px",
                    display: "inline-block",
                  }}
                >
                  &ldquo;Ikuzo, Titan Unit Zero! ⚔️&rdquo;
                </div>
              </div>
            </div>

            {/* Player Controls & Scrubber */}
            <div style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div>
                <div className="eyebrow" style={{ marginBottom: "8px" }}>PLAYBACK CONTROLS</div>
                <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#f8fafc" }}>
                  Hybrid Track Monitor & Scrubber
                </h3>
                <p style={{ fontSize: "13px", color: "#94a3b8", marginTop: "4px" }}>
                  Scrub across clips, verify voice-to-video lip sync, and test background music ducking levels.
                </p>

                {/* Scrubber Slider */}
                <div style={{ marginTop: "24px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "#94a3b8", marginBottom: "6px" }}>
                    <span>Seek Position</span>
                    <span style={{ color: "#38bdf8", fontWeight: 700 }}>{currentTime.toFixed(1)}s / {totalDuration.toFixed(1)}s</span>
                  </div>
                  <input
                    aria-label="Timeline seek position"
                    type="range"
                    min="0"
                    max={totalDuration || 10}
                    step="0.1"
                    value={currentTime}
                    onChange={(e) => setCurrentTime(parseFloat(e.target.value))}
                    style={{ width: "100%", accentColor: "#38bdf8", cursor: "pointer" }}
                  />
                </div>

                {/* Play/Pause Button */}
                <div style={{ marginTop: "16px", display: "flex", gap: "10px" }}>
                  <button
                    type="button"
                    onClick={() => setIsPlaying(!isPlaying)}
                    aria-pressed={isPlaying}
                    className="ds-button primary"
                    style={{ padding: "8px 24px", fontSize: "13px", fontWeight: 700 }}
                  >
                    {isPlaying ? "⏸️ Pause Playback" : "▶️ Play All Tracks"}
                  </button>
                  <button
                    type="button"
                    onClick={() => { setIsPlaying(false); setCurrentTime(0.0); }}
                    className="ds-button"
                    style={{ padding: "8px 16px", fontSize: "13px", backgroundColor: "#1e293b" }}
                  >
                    ⏮️ Reset
                  </button>
                </div>
              </div>

              {/* FFmpeg Render Script Display */}
              {ffmpegCommand && (
                <div style={{ marginTop: "20px", padding: "14px", backgroundColor: "#0b1424", borderRadius: "10px", border: "1px solid #1e293b" }}>
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "#4ade80", marginBottom: "6px" }}>
                    📋 FFmpeg 1080x1920 (9:16) Export Command:
                  </div>
                  <pre style={{ margin: 0, fontSize: "11px", color: "#94a3b8", overflowX: "auto", whiteSpace: "pre-wrap" }}>
                    {ffmpegCommand}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
        <p aria-live="polite" className="sr-only">{compileStatus}</p>

        {/* Import Clip Box */}
        <div className="ds-card" style={{ padding: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
            <div><div className="eyebrow">LOCAL RENDER QUEUE</div><p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "4px" }}>Plans and FFmpeg commands stay in this browser. They do not render or upload automatically.</p></div>
            <div style={{ display: "flex", gap: "8px" }}>{renderJobs.length > 0 && <><button type="button" className="ds-button" onClick={exportRenderQueue} style={{ fontSize: "12px" }}>Export JSON</button><button type="button" className="ds-button" onClick={() => saveRenderJobs([])} style={{ fontSize: "12px" }}>Clear local queue</button></>}<button type="button" className="ds-button" onClick={() => queueImportRef.current?.click()} style={{ fontSize: "12px" }}>Import JSON</button><input ref={queueImportRef} type="file" accept="application/json,.json" className="hidden" onChange={importRenderQueue} /></div>
          </div>
          <div style={{ marginTop: "12px", display: "grid", gap: "8px" }}>
            {renderJobs.length ? renderJobs.map((job) => <div key={job.id} style={{ padding: "10px", border: "1px solid #1e293b", borderRadius: "8px", background: "#0b1424", display: "flex", justifyContent: "space-between", gap: "12px", alignItems: "center" }}><div><strong style={{ color: "#e2e8f0", fontSize: "12px" }}>{job.title}</strong><div style={{ color: "#94a3b8", fontSize: "11px", marginTop: "3px" }}>{job.duration.toFixed(1)}s · {new Date(job.createdAt).toLocaleString()}</div></div><div style={{ display: "flex", gap: "6px" }}><button type="button" onClick={() => { navigator.clipboard?.writeText(job.command).catch(() => undefined); }} className="ds-button" style={{ fontSize: "11px" }}>Copy command</button><button type="button" onClick={() => saveRenderJobs(renderJobs.filter((item) => item.id !== job.id))} className="ds-button" style={{ fontSize: "11px" }}>Remove</button></div></div>) : <p style={{ color: "#64748b", fontSize: "12px" }}>No local render plans yet. Compile a timeline to create one.</p>}
          </div>
        </div>

        {/* Import Clip Box */}
        <div className="ds-card" style={{ padding: "18px" }}>
          <div className="eyebrow" style={{ marginBottom: "8px" }}>IMPORT EXTERNAL AI VIDEO CLIP</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", alignItems: "end" }}>
            <div>
              <label style={{ fontSize: "11px", color: "#94a3b8", display: "block", marginBottom: "4px" }}>Video Title / Scene Name</label>
              <input
                type="text"
                placeholder="e.g. Runway Mech Duel"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: "8px", backgroundColor: "#0b1424", border: "1px solid #1e293b", color: "#f8fafc", fontSize: "12px" }}
              />
            </div>
            <div>
              <label style={{ fontSize: "11px", color: "#94a3b8", display: "block", marginBottom: "4px" }}>External Source URL (MP4/WebM)</label>
              <input
                type="text"
                placeholder="https://.../clip.mp4"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: "8px", backgroundColor: "#0b1424", border: "1px solid #1e293b", color: "#f8fafc", fontSize: "12px" }}
              />
            </div>
            <div>
              <label style={{ fontSize: "11px", color: "#94a3b8", display: "block", marginBottom: "4px" }}>AI Video Engine</label>
              <select
                value={newProvider}
                onChange={(e) => setNewProvider(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: "8px", backgroundColor: "#0b1424", border: "1px solid #1e293b", color: "#f8fafc", fontSize: "12px" }}
              >
                <option value="kling_ai">Kling AI</option>
                <option value="runway_gen3">Runway Gen-3</option>
                <option value="luma_dream_machine">Luma Dream Machine</option>
                <option value="openai_sora">OpenAI Sora</option>
                <option value="pika_labs">Pika Labs</option>
              </select>
            </div>
            <div>
              <label style={{ fontSize: "11px", color: "#94a3b8", display: "block", marginBottom: "4px" }}>Duration (Seconds)</label>
              <input
                type="number"
                step="0.5"
                value={newDuration}
                onChange={(e) => setNewDuration(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: "8px", backgroundColor: "#0b1424", border: "1px solid #1e293b", color: "#f8fafc", fontSize: "12px" }}
              />
            </div>
            <div>
              <button
                type="button"
                onClick={handleAddClip}
                className="ds-button"
                style={{ width: "100%", padding: "7px 12px", fontSize: "12px", backgroundColor: "#1e293b", color: "#38bdf8" }}
              >
                + Add Clip to Timeline
              </button>
            </div>
          </div>
        </div>

        {/* Visual Multi-Track Timeline */}
        <div className="ds-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <div className="eyebrow">ACTIVE MULTI-TRACK TIMELINE</div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "12px", color: "#94a3b8" }}>
              <span>BGM Auto-Ducking:</span>
              <input
                type="range"
                min="0"
                max="100"
                value={bgmVolume}
                onChange={(e) => setBgmVolume(parseInt(e.target.value))}
                style={{ width: "80px" }}
              />
              <span>{bgmVolume}%</span>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px", backgroundColor: "#070b13", padding: "16px", borderRadius: "12px", border: "1px solid #1e293b" }}>
            {/* Track 1: Video Track */}
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div style={{ width: "90px", fontSize: "11px", fontWeight: 700, color: "#38bdf8" }}>🎞️ Video Track</div>
              <div style={{ flex: 1, display: "flex", gap: "8px", overflowX: "auto", paddingBottom: "4px" }}>
                {clips.map((c, i) => (
                  <div
                    key={c.id}
                    style={{
                      flex: `0 0 ${Math.max(c.duration_seconds * 28, 140)}px`,
                      padding: "10px",
                      borderRadius: "8px",
                      backgroundColor: activeClip?.id === c.id ? "#1e3a5f" : "#1e293b",
                      border: activeClip?.id === c.id ? "2px solid #38bdf8" : "1px solid #334155",
                      boxShadow: "0 2px 8px rgba(0,0,0,0.4)",
                      transition: "all 0.2s ease",
                    }}
                  >
                    <div style={{ fontSize: "11px", fontWeight: 600, color: "#f8fafc", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {i + 1}. {c.title}
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginTop: "4px", fontSize: "10px", color: "#94a3b8" }}>
                      <span style={{ textTransform: "uppercase" }}>{c.provider.replace("_", " ")}</span>
                      <span style={{ color: "#38bdf8", fontWeight: 700 }}>{c.duration_seconds}s</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Track 2: Dubbing Audio Track */}
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div style={{ width: "90px", fontSize: "11px", fontWeight: 700, color: "#a855f7" }}>🎙️ Dubbing Voice</div>
              <div style={{ flex: 1, display: "flex", gap: "8px" }}>
                <div style={{ flex: 1, padding: "8px 12px", borderRadius: "8px", backgroundColor: "rgba(168, 85, 247, 0.15)", border: "1px dashed #a855f7", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "11px", color: "#e9d5ff" }}>Voice Binding: <b>Shinji Kazama (ja-JP-KeitaNeural) & Lead Actor</b></span>
                  <span style={{ fontSize: "10px", color: "#c084fc", fontWeight: 700 }}>Synced (Edge-TTS)</span>
                </div>
              </div>
            </div>

            {/* Track 3: BGM Track */}
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div style={{ width: "90px", fontSize: "11px", fontWeight: 700, color: "#22c55e" }}>🎵 Music (BGM)</div>
              <div style={{ flex: 1, display: "flex", gap: "8px" }}>
                <div style={{ flex: 1, padding: "8px 12px", borderRadius: "8px", backgroundColor: "rgba(34, 197, 94, 0.15)", border: "1px solid rgba(34, 197, 94, 0.4)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "11px", color: "#bbf7d0" }}>Track: <b>anime_epic_orchestral_bgm.mp3</b></span>
                  <span style={{ fontSize: "10px", color: "#4ade80", fontWeight: 700 }}>Auto-Ducking: Active (-12dB)</span>
                </div>
              </div>
            </div>

            {/* Track 4: Dynamic Subtitle Track */}
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div style={{ width: "90px", fontSize: "11px", fontWeight: 700, color: "#fbbf24" }}>💬 Subtitles</div>
              <div style={{ flex: 1, display: "flex", gap: "8px" }}>
                <div style={{ flex: 1, padding: "8px 12px", borderRadius: "8px", backgroundColor: "rgba(251, 191, 36, 0.15)", border: "1px solid rgba(251, 191, 36, 0.4)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "11px", color: "#fef08a" }}>Style: <b>Anime Pop Kinetic Typography (ASS/SRT)</b></span>
                  <span style={{ fontSize: "10px", color: "#fcd34d", fontWeight: 700 }}>Whisper Groq Aligned</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
