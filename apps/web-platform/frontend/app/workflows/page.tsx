"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  Play,
  Square,
  RotateCcw,
  Sliders,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  Clapperboard,
  Film,
  Mic,
  Scissors,
  Send,
  ShieldCheck,
  ChevronRight,
  Layers,
  Terminal,
  ArrowRight,
  Settings,
  Cpu,
  Video,
  X,
  Zap,
  Activity,
} from "lucide-react";
import { AppShell } from "../../components/app-shell";

export interface PipelineStage {
  id: string;
  order: number;
  title: string;
  category: "input" | "ai" | "audio" | "video" | "control" | "distribute";
  engine: string;
  description: string;
  enabled: boolean;
  status: "idle" | "running" | "completed" | "bypassed" | "error";
  latency: string;
  config: Record<string, any>;
  icon: React.ComponentType<{ size?: number; className?: string; style?: React.CSSProperties }>;
}

const INITIAL_STAGES: PipelineStage[] = [
  {
    id: "stage-1-ingest",
    order: 1,
    title: "Script & Narrative Ingestion",
    category: "input",
    engine: "Gemini 2.5 Flash Ingest",
    description: "Ingests raw synopsis, script draft, or YouTube link into structured cinematic scenes.",
    enabled: true,
    status: "idle",
    latency: "1.2s",
    config: {
      inputSource: "YouTube / Direct Script Upload",
      targetDuration: "12-15 Mins Recap",
      language: "Burmese Narrative (မြန်မာစကားပြောသံစဉ်)",
      chunkSize: "400 tokens / scene",
    },
    icon: Clapperboard,
  },
  {
    id: "stage-2-breakdown",
    order: 2,
    title: "Scene Breakdown & Shot Planning",
    category: "ai",
    engine: "DeepSeek R1 Narrative Planner",
    description: "Decomposes story into camera setups, visual pacing, lighting keys, and emotion tracks.",
    enabled: true,
    status: "idle",
    latency: "2.8s",
    config: {
      pacingProfile: "Dynamic Action (2.5s - 3.8s / cut)",
      cameraAngles: "Wide establishing, close-up emotive, Dutch tilt",
      emotionKeying: "Suspense, Revelation, Resolution",
    },
    icon: Film,
  },
  {
    id: "stage-3-prompt",
    order: 3,
    title: "Prompt Synthesis & Style Locking",
    category: "ai",
    engine: "Gemini 2.5 Pro Vision Synthesizer",
    description: "Generates photorealistic diffusion prompts with locked seed attributes and lighting formulas.",
    enabled: true,
    status: "idle",
    latency: "1.8s",
    config: {
      aspectRatio: "16:9 & 9:16 Adaptive",
      stylePreset: "Cinematic 35mm Film Grain / Neo-Noir",
      lightingStyle: "Chiaroscuro & Volumetric Neon Fog",
      negativePrompting: "CGI glossy, extra limbs, cartoonish, lowres",
    },
    icon: Sparkles,
  },
  {
    id: "stage-4-lora",
    order: 4,
    title: "Neural Character Consistency (LoRA)",
    category: "ai",
    engine: "ComfyUI LoRA Facial Anchor",
    description: "Enforces identity permanence across frames using custom facial LoRA weights.",
    enabled: true,
    status: "idle",
    latency: "3.4s",
    config: {
      loraWeight: "0.85 (Identity Lock)",
      referenceActors: "Protagonist_Alpha, Antagonist_Omega",
      faceRestoration: "CodeFormer Active",
    },
    icon: Cpu,
  },
  {
    id: "stage-5-flux",
    order: 5,
    title: "Fal.ai / Flux Diffusion Generator",
    category: "video",
    engine: "Flux 1.1 Pro Ultra @ 4K",
    description: "Generates high-fidelity keyframe scenes with realistic textures and motion vector cues.",
    enabled: true,
    status: "idle",
    latency: "4.5s",
    config: {
      inferenceSteps: "28 Steps",
      guidanceScale: "3.5",
      outputResolution: "3840 x 2160 (4K UHD)",
      batchSize: "4 Parallel Frames",
    },
    icon: Video,
  },
  {
    id: "stage-6-elevenlabs",
    order: 6,
    title: "ElevenLabs Voice & Audio Layer",
    category: "audio",
    engine: "ElevenLabs Multilingual v2",
    description: "Synthesizes Burmese narrative voiceover, ambient soundscapes, and ducked cinematic BGM.",
    enabled: true,
    status: "idle",
    latency: "2.1s",
    config: {
      voiceModel: "my-MM-ThihaNeural / ElevenLabs Studio",
      stability: "0.68",
      similarityBoost: "0.82",
      bgmDuckingLevel: "-14dB below narration",
    },
    icon: Mic,
  },
  {
    id: "stage-7-review",
    order: 7,
    title: "Director Review Gate",
    category: "control",
    engine: "Human-in-the-Loop Sign-off",
    description: "Interactive visual checkpoint for final audio/video grading. Bypassed for auto-batch mode.",
    enabled: false,
    status: "bypassed",
    latency: "0.0s (Bypassed)",
    config: {
      requireApproval: false,
      autoBypass: true,
      bypassTarget: "Stage 8: Final 4K Render",
      notifyTelegramOnWait: true,
    },
    icon: ShieldCheck,
  },
  {
    id: "stage-8-render",
    order: 8,
    title: "Final 4K Render & Video Packager",
    category: "distribute",
    engine: "FFmpeg GPU Cluster + Telegram",
    description: "Stitches synced audio and video, burns karaoke Burmese subtitles, and pushes to Telegram.",
    enabled: true,
    status: "idle",
    latency: "5.1s",
    config: {
      codec: "H.265 / HEVC NVENC",
      bitrate: "18 Mbps Constant",
      subtitleStyle: "Cyberpunk Neon Stroke (Burmese Padauk)",
      exportTarget: "Telegram Topic 6 · Releases",
    },
    icon: Send,
  },
];

export default function WorkflowsPage() {
  const [stages, setStages] = useState<PipelineStage[]>(INITIAL_STAGES);
  const [selectedStageId, setSelectedStageId] = useState<string | null>("stage-1-ingest");
  const [isSimulating, setIsSimulating] = useState(false);
  const [simStep, setSimStep] = useState<number>(-1);
  const [logs, setLogs] = useState<
    Array<{ timestamp: string; stageTitle: string; message: string; type: "info" | "success" | "warn" | "bypass" }>
  >([
    {
      timestamp: "18:20:00",
      stageTitle: "SYSTEM",
      message: "Narrativ Forge 8-Stage Cinematic Production Pipeline initialized. Ready for batch execution.",
      type: "info",
    },
    {
      timestamp: "18:20:01",
      stageTitle: "ROUTING",
      message: "Stage 7 [Director Review Gate] disabled: Auto-bypass routing directly to Stage 8 enabled.",
      type: "bypass",
    },
  ]);

  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // Toggle stage enabled/disabled
  const handleToggleStage = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setStages((prev) =>
      prev.map((stage) => {
        if (stage.id !== id) return stage;
        const newEnabled = !stage.enabled;
        const newStatus = !newEnabled ? "bypassed" : "idle";

        addLog(
          stage.title,
          newEnabled
            ? `Stage re-enabled into active pipeline.`
            : `Stage bypassed. Downstream route will auto-bridge past this node.`,
          newEnabled ? "info" : "bypass"
        );

        return {
          ...stage,
          enabled: newEnabled,
          status: newStatus,
          latency: !newEnabled ? "0.0s (Bypassed)" : stage.latency,
        };
      })
    );
  };

  const addLog = (
    stageTitle: string,
    message: string,
    type: "info" | "success" | "warn" | "bypass" = "info"
  ) => {
    const time = new Date().toTimeString().split(" ")[0];
    setLogs((prev) => [...prev, { timestamp: time, stageTitle, message, type }]);
  };

  // Run live simulation through all stages
  const runSimulation = async () => {
    if (isSimulating) return;
    setIsSimulating(true);
    setSimStep(0);

    // Reset status
    setStages((prev) =>
      prev.map((s) => ({
        ...s,
        status: !s.enabled ? "bypassed" : "idle",
      }))
    );

    addLog("EXECUTION", "Starting end-to-end Cinematic Pipeline simulation...", "info");

    for (let i = 0; i < stages.length; i++) {
      const current = stages[i];
      setSimStep(i);

      if (!current.enabled) {
        setStages((prev) =>
          prev.map((s, idx) => (idx === i ? { ...s, status: "bypassed" } : s))
        );
        addLog(
          current.title,
          `Stage is disabled. Auto-bypassing to next active stage in 200ms...`,
          "bypass"
        );
        await new Promise((r) => setTimeout(r, 400));
        continue;
      }

      // Mark running
      setStages((prev) =>
        prev.map((s, idx) => (idx === i ? { ...s, status: "running" } : s))
      );
      addLog(current.title, `Executing [${current.engine}]...`, "info");

      // Simulate work duration
      await new Promise((r) => setTimeout(r, 900));

      // Mark completed
      setStages((prev) =>
        prev.map((s, idx) => (idx === i ? { ...s, status: "completed" } : s))
      );
      addLog(current.title, `Completed successfully in ${current.latency}.`, "success");
    }

    addLog("PIPELINE", "All active stages completed. Master 4K video rendered and queued.", "success");
    setIsSimulating(false);
    setSimStep(-1);
  };

  const resetPipeline = () => {
    setIsSimulating(false);
    setSimStep(-1);
    setStages(INITIAL_STAGES);
    setLogs([
      {
        timestamp: new Date().toTimeString().split(" ")[0],
        stageTitle: "SYSTEM",
        message: "Pipeline state reset to default configuration.",
        type: "info",
      },
    ]);
  };

  const selectedStage = stages.find((s) => s.id === selectedStageId) || stages[0];
  const activeCount = stages.filter((s) => s.enabled).length;

  return (
    <AppShell title="Cinematic Pipeline Canvas">
      <div style={{ display: "grid", gap: "24px", paddingBottom: "40px" }}>
        {/* Top Control Header */}
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
                <Zap size={13} />
                ZERO-CODE PIPELINE
              </span>
              <span style={{ color: "#9aa9b5", fontSize: "12px" }}>
                Auto-Bypass Routing · Telemetry Connected
              </span>
            </div>
            <h2 style={{ fontSize: "22px", fontWeight: 800, color: "#f4f7f8", margin: 0 }}>
              Automated Movie Recap & Storyboard Pipeline
            </h2>
            <p style={{ color: "#9aa9b5", fontSize: "13px", margin: "6px 0 0" }}>
              Active Stages: <strong style={{ color: "#d8ff4f" }}>{activeCount}</strong> / {stages.length} ·
              Bypass Modes: <strong style={{ color: "#f59e0b" }}>{stages.length - activeCount} Bypassed</strong> ·
              Cluster Latency: <strong style={{ color: "#f4f7f8" }}>~2.6s / Scene</strong>
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <button
              onClick={resetPipeline}
              disabled={isSimulating}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "10px 16px",
                borderRadius: "10px",
                border: "1px solid #26323d",
                background: "#17212b",
                color: "#c5d0d8",
                fontSize: "13px",
                fontWeight: 600,
                cursor: isSimulating ? "not-allowed" : "pointer",
                transition: "all 0.15s ease",
              }}
            >
              <RotateCcw size={15} />
              Reset
            </button>

            <button
              onClick={runSimulation}
              disabled={isSimulating}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "10px 20px",
                borderRadius: "10px",
                border: "none",
                background: isSimulating ? "#3a4a57" : "#d8ff4f",
                color: isSimulating ? "#9aa9b5" : "#090c10",
                fontSize: "13px",
                fontWeight: 800,
                cursor: isSimulating ? "not-allowed" : "pointer",
                boxShadow: isSimulating ? "none" : "0 0 20px rgba(216, 255, 79, 0.35)",
                transition: "all 0.15s ease",
              }}
            >
              {isSimulating ? (
                <>
                  <Square size={15} style={{ animation: "pulse 1s infinite" }} />
                  Processing Stage {simStep + 1}...
                </>
              ) : (
                <>
                  <Play size={15} fill="#090c10" />
                  Run Live Pipeline
                </>
              )}
            </button>
          </div>
        </section>

        {/* Pipeline Layout (Stages on Left, Inspector on Right) */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: "24px" }}>
          {/* Main Stages Column */}
          <div style={{ display: "grid", gap: "14px" }}>
            {stages.map((stage, idx) => {
              const Icon = stage.icon;
              const isSelected = stage.id === selectedStageId;
              const isCurrentlyRunning = stage.status === "running";
              const isCompleted = stage.status === "completed";
              const isBypassed = stage.status === "bypassed" || !stage.enabled;

              return (
                <div key={stage.id} style={{ display: "grid", gap: "10px" }}>
                  <div
                    onClick={() => setSelectedStageId(stage.id)}
                    style={{
                      background: isSelected
                        ? "linear-gradient(135deg, rgba(216,255,79,0.06), #111820)"
                        : "#111820",
                      border: `1px solid ${
                        isSelected
                          ? "#d8ff4f"
                          : isCurrentlyRunning
                          ? "#d8ff4f"
                          : isBypassed
                          ? "rgba(245, 158, 11, 0.35)"
                          : "#26323d"
                      }`,
                      borderRadius: "14px",
                      padding: "18px 20px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: "16px",
                      cursor: "pointer",
                      transition: "all 0.18s ease",
                      opacity: isBypassed ? 0.72 : 1,
                      boxShadow: isSelected
                        ? "0 0 24px rgba(216, 255, 79, 0.08)"
                        : "none",
                    }}
                  >
                    {/* Stage Left: Icon & Info */}
                    <div style={{ display: "flex", alignItems: "center", gap: "16px", minWidth: 0 }}>
                      <div
                        style={{
                          width: "44px",
                          height: "44px",
                          borderRadius: "12px",
                          display: "grid",
                          placeItems: "center",
                          flexShrink: 0,
                          background: isBypassed
                            ? "rgba(245, 158, 11, 0.12)"
                            : isCurrentlyRunning
                            ? "rgba(216, 255, 79, 0.2)"
                            : isCompleted
                            ? "rgba(16, 185, 129, 0.15)"
                            : "rgba(255, 255, 255, 0.05)",
                          color: isBypassed
                            ? "#f59e0b"
                            : isCurrentlyRunning
                            ? "#d8ff4f"
                            : isCompleted
                            ? "#10b981"
                            : "#c5d0d8",
                          border: `1px solid ${
                            isBypassed
                              ? "rgba(245, 158, 11, 0.3)"
                              : isCurrentlyRunning
                              ? "#d8ff4f"
                              : "rgba(255,255,255,0.08)"
                          }`,
                        }}
                      >
                        <Icon size={20} />
                      </div>

                      <div style={{ minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                          <span
                            style={{
                              fontSize: "10px",
                              fontWeight: 800,
                              textTransform: "uppercase",
                              letterSpacing: "0.08em",
                              color: "#9aa9b5",
                            }}
                          >
                            STAGE {stage.order}
                          </span>
                          <span
                            style={{
                              fontSize: "10px",
                              fontWeight: 700,
                              padding: "2px 7px",
                              borderRadius: "6px",
                              background: "#17212b",
                              color: "#d8ff4f",
                              border: "1px solid #26323d",
                            }}
                          >
                            {stage.engine}
                          </span>
                        </div>
                        <h3
                          style={{
                            fontSize: "15px",
                            fontWeight: 700,
                            color: isBypassed ? "#9aa9b5" : "#f4f7f8",
                            margin: "4px 0 2px",
                            textDecoration: isBypassed ? "line-through" : "none",
                          }}
                        >
                          {stage.title}
                        </h3>
                        <p
                          style={{
                            fontSize: "12px",
                            color: "#9aa9b5",
                            margin: 0,
                            whiteSpace: "nowrap",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            maxWidth: "460px",
                          }}
                        >
                          {stage.description}
                        </p>
                      </div>
                    </div>

                    {/* Stage Right: Status, Latency & Bypass Switch */}
                    <div style={{ display: "flex", alignItems: "center", gap: "16px", flexShrink: 0 }}>
                      {/* Status Badge */}
                      {isCurrentlyRunning && (
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "6px",
                            padding: "4px 10px",
                            borderRadius: "999px",
                            fontSize: "11px",
                            fontWeight: 700,
                            background: "rgba(216, 255, 79, 0.15)",
                            color: "#d8ff4f",
                            border: "1px solid rgba(216, 255, 79, 0.3)",
                            animation: "pulse 1.5s infinite",
                          }}
                        >
                          <Activity size={12} />
                          Running...
                        </span>
                      )}

                      {isCompleted && (
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "6px",
                            padding: "4px 10px",
                            borderRadius: "999px",
                            fontSize: "11px",
                            fontWeight: 700,
                            background: "rgba(16, 185, 129, 0.15)",
                            color: "#10b981",
                            border: "1px solid rgba(16, 185, 129, 0.3)",
                          }}
                        >
                          <CheckCircle2 size={12} />
                          Done ({stage.latency})
                        </span>
                      )}

                      {isBypassed && (
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "6px",
                            padding: "4px 10px",
                            borderRadius: "999px",
                            fontSize: "11px",
                            fontWeight: 700,
                            background: "rgba(245, 158, 11, 0.12)",
                            color: "#f59e0b",
                            border: "1px solid rgba(245, 158, 11, 0.3)",
                          }}
                        >
                          BYPASS ROUTE
                        </span>
                      )}

                      {!isCurrentlyRunning && !isCompleted && !isBypassed && (
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "4px",
                            fontSize: "12px",
                            color: "#9aa9b5",
                          }}
                        >
                          <Clock size={12} />
                          {stage.latency}
                        </span>
                      )}

                      {/* Enable / Disable Switch Toggle */}
                      <div
                        onClick={(e) => handleToggleStage(stage.id, e)}
                        title={stage.enabled ? "Click to bypass stage" : "Click to enable stage"}
                        style={{
                          width: "44px",
                          height: "24px",
                          borderRadius: "999px",
                          background: stage.enabled ? "#d8ff4f" : "#26323d",
                          padding: "2px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: stage.enabled ? "flex-end" : "flex-start",
                          cursor: "pointer",
                          transition: "all 0.2s ease",
                        }}
                      >
                        <div
                          style={{
                            width: "20px",
                            height: "20px",
                            borderRadius: "50%",
                            background: stage.enabled ? "#090c10" : "#9aa9b5",
                            boxShadow: "0 1px 3px rgba(0,0,0,0.4)",
                            transition: "all 0.2s ease",
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Flow Connector Line (Between Nodes) */}
                  {idx < stages.length - 1 && (
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        height: "18px",
                      }}
                    >
                      <div
                        style={{
                          width: "2px",
                          height: "100%",
                          background: isBypassed
                            ? "repeating-linear-gradient(to bottom, #f59e0b 0, #f59e0b 4px, transparent 4px, transparent 8px)"
                            : isCompleted
                            ? "#10b981"
                            : "#26323d",
                        }}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Right Column: Node Inspector & Telemetry Log */}
          <div style={{ display: "grid", gap: "20px", alignContent: "start" }}>
            {/* Stage Inspector Panel */}
            <div
              style={{
                background: "#111820",
                border: "1px solid #26323d",
                borderRadius: "16px",
                padding: "20px",
                boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  paddingBottom: "14px",
                  borderBottom: "1px solid #26323d",
                  marginBottom: "16px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <Sliders size={16} style={{ color: "#d8ff4f" }} />
                  <span style={{ fontSize: "14px", fontWeight: 800, color: "#f4f7f8" }}>
                    Stage Inspector
                  </span>
                </div>
                <span
                  style={{
                    fontSize: "11px",
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: "999px",
                    background: selectedStage.enabled ? "rgba(216,255,79,0.12)" : "rgba(245,158,11,0.12)",
                    color: selectedStage.enabled ? "#d8ff4f" : "#f59e0b",
                    border: `1px solid ${
                      selectedStage.enabled ? "rgba(216,255,79,0.25)" : "rgba(245,158,11,0.25)"
                    }`,
                  }}
                >
                  Stage {selectedStage.order}
                </span>
              </div>

              <div style={{ display: "grid", gap: "12px" }}>
                <div>
                  <label style={{ fontSize: "11px", fontWeight: 700, color: "#9aa9b5", textTransform: "uppercase" }}>
                    Selected Module
                  </label>
                  <div style={{ fontSize: "14px", fontWeight: 700, color: "#f4f7f8", marginTop: "4px" }}>
                    {selectedStage.title}
                  </div>
                </div>

                <div>
                  <label style={{ fontSize: "11px", fontWeight: 700, color: "#9aa9b5", textTransform: "uppercase" }}>
                    Engine & Provider
                  </label>
                  <div style={{ fontSize: "13px", color: "#d8ff4f", marginTop: "4px", fontWeight: 600 }}>
                    {selectedStage.engine}
                  </div>
                </div>

                <div>
                  <label style={{ fontSize: "11px", fontWeight: 700, color: "#9aa9b5", textTransform: "uppercase" }}>
                    Node Status
                  </label>
                  <div style={{ fontSize: "13px", color: "#c5d0d8", marginTop: "4px" }}>
                    Status: <strong style={{ color: selectedStage.enabled ? "#10b981" : "#f59e0b" }}>{selectedStage.status.toUpperCase()}</strong> · Latency: {selectedStage.latency}
                  </div>
                </div>

                <div style={{ marginTop: "8px", borderTop: "1px solid #26323d", paddingTop: "12px" }}>
                  <label style={{ fontSize: "11px", fontWeight: 700, color: "#9aa9b5", textTransform: "uppercase" }}>
                    Config Parameters
                  </label>
                  <div
                    style={{
                      background: "#090c10",
                      border: "1px solid #26323d",
                      borderRadius: "10px",
                      padding: "12px",
                      marginTop: "6px",
                      fontSize: "12px",
                      fontFamily: "monospace",
                      display: "grid",
                      gap: "8px",
                    }}
                  >
                    {Object.entries(selectedStage.config).map(([key, val]) => (
                      <div key={key} style={{ display: "flex", justifyContent: "space-between", gap: "8px" }}>
                        <span style={{ color: "#9aa9b5" }}>{key}:</span>
                        <span style={{ color: "#d8ff4f", textAlign: "right", wordBreak: "break-all" }}>
                          {String(val)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Live Telemetry Log Terminal */}
            <div
              style={{
                background: "#090c10",
                border: "1px solid #26323d",
                borderRadius: "16px",
                padding: "16px",
                display: "grid",
                gap: "10px",
                boxShadow: "0 8px 32px rgba(0,0,0,0.35)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  borderBottom: "1px solid #26323d",
                  paddingBottom: "10px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <Terminal size={15} style={{ color: "#d8ff4f" }} />
                  <span style={{ fontSize: "12px", fontWeight: 800, color: "#f4f7f8", textTransform: "uppercase" }}>
                    Pipeline Telemetry
                  </span>
                </div>
                <span
                  style={{
                    width: "8px",
                    height: "8px",
                    borderRadius: "50%",
                    background: isSimulating ? "#d8ff4f" : "#10b981",
                    boxShadow: isSimulating ? "0 0 10px #d8ff4f" : "none",
                  }}
                />
              </div>

              <div
                style={{
                  height: "240px",
                  overflowY: "auto",
                  display: "grid",
                  gap: "6px",
                  fontSize: "11px",
                  fontFamily: "monospace",
                  color: "#c5d0d8",
                  paddingRight: "4px",
                }}
              >
                {logs.map((log, i) => (
                  <div key={i} style={{ lineHeight: 1.45 }}>
                    <span style={{ color: "#71818d" }}>[{log.timestamp}]</span>{" "}
                    <span
                      style={{
                        fontWeight: 700,
                        color:
                          log.type === "success"
                            ? "#10b981"
                            : log.type === "warn"
                            ? "#f43f5e"
                            : log.type === "bypass"
                            ? "#f59e0b"
                            : "#d8ff4f",
                      }}
                    >
                      [{log.stageTitle}]
                    </span>{" "}
                    <span>{log.message}</span>
                  </div>
                ))}
                <div ref={terminalEndRef} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
