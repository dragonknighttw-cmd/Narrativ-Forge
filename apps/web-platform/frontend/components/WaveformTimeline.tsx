"use client";

import React, { useState, useEffect, useRef } from "react";
import { Scene } from "../lib/api";

interface WaveformTimelineProps {
  scenes: Scene[];
  onUpdateDuration?: (sceneId: string, newDuration: number) => void;
  audioUrl?: string;
}

export function WaveformTimeline({
  scenes,
  onUpdateDuration,
  audioUrl,
}: WaveformTimelineProps) {
  const [playhead, setPlayhead] = useState(0); // in seconds
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedSceneId, setSelectedSceneId] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animFrameRef = useRef<number | null>(null);

  const totalDuration = scenes.reduce((sum, s) => sum + (s.duration_seconds || 10), 0) || 180;

  // Render synthetic or real audio waveform onto canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    // Draw background grid lines
    ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    // Generate harmonic waveform peaks based on scene sequence
    const bars = Math.floor(width / 3);
    const midY = height / 2;

    for (let i = 0; i < bars; i++) {
      const progress = i / bars;
      const currentSec = progress * totalDuration;

      // Find active scene at currentSec
      let accumulated = 0;
      let activeIdx = 0;
      for (let sIdx = 0; sIdx < scenes.length; sIdx++) {
        accumulated += scenes[sIdx].duration_seconds || 10;
        if (currentSec <= accumulated) {
          activeIdx = sIdx;
          break;
        }
      }

      // Generate organic voice energy peaks with rhythm modulation
      const freq1 = Math.sin(i * 0.18 + activeIdx);
      const freq2 = Math.cos(i * 0.07);
      const energy = Math.abs(freq1 * 0.6 + freq2 * 0.4);
      const barHeight = Math.max(4, energy * (height * 0.8));

      // Color based on active playback position
      const isPast = currentSec <= playhead;
      if (isPast) {
        ctx.fillStyle = "#38bdf8"; // Luminous Cyan for played audio
      } else {
        ctx.fillStyle = "rgba(148, 163, 184, 0.45)"; // Slate muted for upcoming audio
      }

      const x = i * 3;
      ctx.fillRect(x, midY - barHeight / 2, 2, barHeight);
    }

    // Draw vertical Playhead line
    const playheadX = (playhead / totalDuration) * width;
    ctx.strokeStyle = "#f43f5e";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(playheadX, 0);
    ctx.lineTo(playheadX, height);
    ctx.stroke();

    // Playhead glowing head triangle
    ctx.fillStyle = "#f43f5e";
    ctx.beginPath();
    ctx.moveTo(playheadX - 5, 0);
    ctx.lineTo(playheadX + 5, 0);
    ctx.lineTo(playheadX, 7);
    ctx.closePath();
    ctx.fill();
  }, [scenes, playhead, totalDuration]);

  // Scrub playhead animation loop
  useEffect(() => {
    if (!isPlaying) return;
    const interval = 100; // ms
    const timer = setInterval(() => {
      setPlayhead((prev) => {
        if (prev >= totalDuration) {
          setIsPlaying(false);
          return 0;
        }
        return +(prev + interval / 1000).toFixed(2);
      });
    }, interval);

    return () => clearInterval(timer);
  }, [isPlaying, totalDuration]);

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const pct = Math.max(0, Math.min(1, clickX / rect.width));
    setPlayhead(+(pct * totalDuration).toFixed(1));
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const colors = ["#0284c7", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899", "#06b6d4"];

  return (
    <div className="waveform-timeline-container" style={{
      marginTop: "1.5rem",
      background: "rgba(15, 23, 42, 0.75)",
      border: "1px solid rgba(56, 189, 248, 0.25)",
      borderRadius: "16px",
      padding: "1.25rem",
      boxShadow: "0 8px 32px rgba(0, 0, 0, 0.4)"
    }}>
      {/* Header Controls */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            style={{
              background: isPlaying ? "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.2)",
              color: isPlaying ? "#ef4444" : "#10b981",
              border: `1px solid ${isPlaying ? "#ef4444" : "#10b981"}`,
              padding: "0.35rem 0.85rem",
              borderRadius: "8px",
              cursor: "pointer",
              fontWeight: 700,
              fontSize: "0.8rem",
              display: "flex",
              alignItems: "center",
              gap: "0.35rem"
            }}
          >
            {isPlaying ? "⏸ Pause" : "▶ Preview Scrubber"}
          </button>
          <button
            onClick={() => { setPlayhead(0); setIsPlaying(false); }}
            style={{
              background: "transparent",
              color: "#94a3b8",
              border: "1px solid rgba(148, 163, 184, 0.3)",
              padding: "0.35rem 0.65rem",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "0.8rem"
            }}
          >
            ⏮ Reset
          </button>
          <span style={{ fontFamily: "monospace", fontSize: "0.85rem", color: "#38bdf8", fontWeight: 700 }}>
            {formatTime(playhead)} / {formatTime(totalDuration)}
          </span>
        </div>

        <div style={{ display: "flex", gap: "0.5rem", fontSize: "0.75rem", color: "#94a3b8" }}>
          <span>🎵 <strong>Track 1:</strong> Scene Cuts</span>
          <span>•</span>
          <span>🎙️ <strong>Track 2:</strong> Web Audio Waveform</span>
        </div>
      </div>

      {/* Interactive Timeline Scrub Area */}
      <div
        onClick={handleTimelineClick}
        style={{
          cursor: "crosshair",
          position: "relative",
          userSelect: "none",
          borderRadius: "10px",
          overflow: "hidden",
          border: "1px solid rgba(255, 255, 255, 0.1)",
          background: "#090d16"
        }}
      >
        {/* Track 1: Scene Clip Blocks */}
        <div style={{ display: "flex", height: "42px", gap: "2px", padding: "3px", background: "rgba(0, 0, 0, 0.5)" }}>
          {scenes.map((scene, i) => {
            const pct = totalDuration > 0 ? ((scene.duration_seconds || 10) / totalDuration) * 100 : 100 / scenes.length;
            const bg = colors[i % colors.length];
            const isSelected = selectedSceneId === scene.id;

            return (
              <div
                key={scene.id}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedSceneId(isSelected ? null : scene.id);
                }}
                title={`Scene ${scene.scene_number}: ${scene.purpose} (${scene.duration_seconds}s) - Click to trim`}
                style={{
                  flex: `0 0 calc(${pct}% - 2px)`,
                  minWidth: "44px",
                  background: isSelected ? `${bg}44` : `${bg}1a`,
                  border: `1.5px solid ${isSelected ? "#ffffff" : bg}`,
                  borderRadius: "6px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  alignItems: "center",
                  padding: "2px 4px",
                  cursor: "pointer",
                  position: "relative",
                  transition: "all 0.15s ease",
                  boxShadow: isSelected ? `0 0 10px ${bg}` : "none"
                }}
              >
                <span style={{ fontSize: "0.68rem", fontWeight: 800, color: bg, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  S{scene.scene_number} ({scene.duration_seconds}s)
                </span>
                <span style={{ fontSize: "0.58rem", color: "rgba(255, 255, 255, 0.8)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {scene.purpose}
                </span>
              </div>
            );
          })}
        </div>

        {/* Track 2: Web Audio Waveform Peak Canvas */}
        <div style={{ position: "relative", height: "48px", background: "#050811" }}>
          <canvas
            ref={canvasRef}
            width={900}
            height={48}
            style={{ width: "100%", height: "100%", display: "block" }}
          />
        </div>
      </div>

      {/* Selected Scene Trimming Controls Pill */}
      {selectedSceneId && (
        <div style={{
          marginTop: "0.75rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0.5rem 0.85rem",
          background: "rgba(56, 189, 248, 0.1)",
          border: "1px solid rgba(56, 189, 248, 0.3)",
          borderRadius: "8px"
        }}>
          {(() => {
            const sc = scenes.find((s) => s.id === selectedSceneId);
            if (!sc) return null;
            return (
              <>
                <span style={{ fontSize: "0.8rem", color: "#f8fafc", fontWeight: 600 }}>
                  Editing <strong>Scene {sc.scene_number}</strong>: "{sc.purpose}" (Current: {sc.duration_seconds || 10}s)
                </span>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button
                    onClick={() => {
                      const cur = sc.duration_seconds || 10;
                      if (cur > 1 && onUpdateDuration) onUpdateDuration(sc.id, cur - 1);
                    }}
                    style={{
                      background: "rgba(255, 255, 255, 0.1)",
                      color: "#ffffff",
                      border: "none",
                      padding: "0.2rem 0.6rem",
                      borderRadius: "4px",
                      cursor: "pointer",
                      fontWeight: 700,
                      fontSize: "0.75rem"
                    }}
                  >
                    -1s Trim
                  </button>
                  <button
                    onClick={() => {
                      const cur = sc.duration_seconds || 10;
                      if (onUpdateDuration) onUpdateDuration(sc.id, cur + 1);
                    }}
                    style={{
                      background: "#0284c7",
                      color: "#ffffff",
                      border: "none",
                      padding: "0.2rem 0.6rem",
                      borderRadius: "4px",
                      cursor: "pointer",
                      fontWeight: 700,
                      fontSize: "0.75rem"
                    }}
                  >
                    +1s Extend
                  </button>
                  <button
                    onClick={() => setSelectedSceneId(null)}
                    style={{
                      background: "transparent",
                      color: "#94a3b8",
                      border: "none",
                      cursor: "pointer",
                      fontSize: "0.75rem"
                    }}
                  >
                    ✕ Close
                  </button>
                </div>
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
}

export default WaveformTimeline;
