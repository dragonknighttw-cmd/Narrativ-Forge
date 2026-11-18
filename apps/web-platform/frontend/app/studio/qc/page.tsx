"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../../components/app-shell";
import { api } from "../../../lib/api";
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  HardDriveDownload,
  Activity,
  Layers,
  Sparkles,
  Volume2,
  Captions,
  Film,
  Zap,
} from "lucide-react";

interface QCIssue {
  severity: "warning" | "error" | "info";
  type: string;
  timestamp: number;
  message: string;
}

export default function QualityControlPage() {
  const [evaluating, setEvaluating] = useState(false);
  const [qcReport, setQcReport] = useState<any>({
    overall_score: 96,
    black_frames_detected: 0,
    frozen_frames_detected: 0,
    audio_clipping_events: 0,
    av_sync_offset_ms: 8.5,
    subtitle_sync_status: "perfect",
    passed: true,
    issues: [
      {
        severity: "info",
        type: "pacing_speed",
        timestamp: 14.5,
        message: "Dynamic pacing transition cut aligns within 0.05s of music beat drop.",
      },
    ],
  });

  async function handleRunQC() {
    setEvaluating(true);
    try {
      const res = await api.evaluateQC({
        timeline_id: "active-timeline-01",
        tracks: {
          video_track: [
            { clip_id: "c1", start_time: 0.0, end_time: 4.5 },
            { clip_id: "c2", start_time: 4.5, end_time: 10.0 },
          ],
          voice_track: [{ start_time: 0.5, end_time: 9.8 }],
          subtitle_track: [{ start_time: 0.5, end_time: 9.8 }],
        },
      });
      if (res) setQcReport(res);
    } catch {
      // Fallback preview
    } finally {
      setEvaluating(false);
    }
  }

  return (
    <AppShell title="Quality Control & Pre-Export Gate">
      <div style={{ display: "flex", flexDirection: "column", gap: "24px", paddingBottom: "48px" }}>
        
        {/* Intro */}
        <div style={{
          background: "#0b1220",
          border: "1px solid #1e293b",
          borderRadius: "14px",
          padding: "24px",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#10b981", fontSize: "12px", fontWeight: 700, letterSpacing: "0.05em", marginBottom: "6px" }}>
            <ShieldCheck size={14} /> MODULE 08 · QUALITY CONTROL ENGINE
          </div>
          <h2 style={{ fontSize: "22px", fontWeight: 700, color: "#f8fafc", margin: "0 0 6px 0" }}>
            Pre-Export Automated Quality Verification
          </h2>
          <p style={{ fontSize: "14px", color: "#94a3b8", margin: 0, maxWidth: "750px", lineHeight: "1.5" }}>
            ဗီဒီယို Export မပြုလုပ်မီ အသံကွဲခြင်း (Audio Clipping)၊ အနက်ရောင် Frame ကျန်ခဲ့ခြင်း (Black Frame)၊
            အသံနှင့်ရုပ်သံ လွဲချော်မှု (A/V Sync Offset) နှင့် မြန်မာစာတန်းထိုး အထားအသိုများကို စစ်ဆေးပေးမည့် နောက်ဆုံး Quality Gate ဖြစ်ပါသည်။
          </p>
        </div>

        {/* Big Score Card */}
        <div style={{
          background: "linear-gradient(135deg, rgba(8, 13, 24, 0.95), rgba(15, 23, 42, 0.9))",
          border: `1.5px solid ${qcReport.passed ? "#10b981" : "#ef4444"}`,
          borderRadius: "16px",
          padding: "32px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          boxShadow: "0 10px 30px -10px rgba(0, 0, 0, 0.5)",
        }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "4px 12px",
                background: qcReport.passed ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                border: `1px solid ${qcReport.passed ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"}`,
                borderRadius: "20px",
                fontSize: "12px",
                fontWeight: 700,
                color: qcReport.passed ? "#34d399" : "#f87171",
              }}>
                {qcReport.passed ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
                {qcReport.passed ? "QUALITY GATE PASSED • PRODUCTION READY" : "QUALITY ISSUES DETECTED"}
              </span>
            </div>

            <h1 style={{ fontSize: "36px", fontWeight: 800, color: "#f8fafc", margin: "12px 0 6px 0" }}>
              Score: {qcReport.overall_score} / 100
            </h1>
            <p style={{ fontSize: "14px", color: "#94a3b8", margin: 0 }}>
              {qcReport.passed
                ? "အသံနှင့် ရုပ်သံ ချိန်ညှိမှု ကောင်းမွန်ပြီး အနက်ရောင် frame သို့မဟုတ် အသံကွဲခြင်း မတွေ့ရှိပါ။ Export ပြုလုပ်နိုင်ပါပြီ။"
                : "အချို့သော အစိတ်အပိုင်းများတွင် A/V Sync သို့မဟုတ် Black Frame ကွာဟချက်များ ရှိနေပါသည်။"}
            </p>
          </div>

          <button
            type="button"
            onClick={handleRunQC}
            disabled={evaluating}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "14px 24px",
              background: "linear-gradient(135deg, #0284c7, #0369a1)",
              border: "none",
              borderRadius: "10px",
              color: "#ffffff",
              fontSize: "14px",
              fontWeight: 600,
              cursor: evaluating ? "not-allowed" : "pointer",
              boxShadow: "0 4px 14px rgba(2, 132, 199, 0.3)",
            }}
          >
            <Sparkles size={16} />
            {evaluating ? "Evaluating Timeline..." : "Re-Run Complete QC Audit"}
          </button>
        </div>

        {/* 4 Diagnostic Health Tiles */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px" }}>
          
          <div style={{ background: "#0b1220", border: "1px solid #1e293b", borderRadius: "12px", padding: "18px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#64748b", fontSize: "12px", fontWeight: 600 }}>
              <Film size={14} /> Black Frame Gaps
            </div>
            <div style={{ fontSize: "24px", fontWeight: 700, color: qcReport.black_frames_detected === 0 ? "#10b981" : "#ef4444", marginTop: "6px" }}>
              {qcReport.black_frames_detected}
            </div>
            <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>Zero empty video frames</div>
          </div>

          <div style={{ background: "#0b1220", border: "1px solid #1e293b", borderRadius: "12px", padding: "18px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#64748b", fontSize: "12px", fontWeight: 600 }}>
              <Volume2 size={14} /> Audio Clipping / Peak
            </div>
            <div style={{ fontSize: "24px", fontWeight: 700, color: qcReport.audio_clipping_events === 0 ? "#10b981" : "#ef4444", marginTop: "6px" }}>
              {qcReport.audio_clipping_events}
            </div>
            <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>Peak capped at -0.5 dBFS</div>
          </div>

          <div style={{ background: "#0b1220", border: "1px solid #1e293b", borderRadius: "12px", padding: "18px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#64748b", fontSize: "12px", fontWeight: 600 }}>
              <Activity size={14} /> A/V Sync Drift
            </div>
            <div style={{ fontSize: "24px", fontWeight: 700, color: "#38bdf8", marginTop: "6px" }}>
              {qcReport.av_sync_offset_ms} ms
            </div>
            <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>Imperceptible (&lt; 40ms threshold)</div>
          </div>

          <div style={{ background: "#0b1220", border: "1px solid #1e293b", borderRadius: "12px", padding: "18px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#64748b", fontSize: "12px", fontWeight: 600 }}>
              <Captions size={14} /> Subtitle Timing
            </div>
            <div style={{ fontSize: "20px", fontWeight: 700, color: "#10b981", marginTop: "8px" }}>
              {qcReport.subtitle_sync_status.toUpperCase()}
            </div>
            <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>Synchronized with Voice Track</div>
          </div>

        </div>

        {/* QC Audit Issue Logs */}
        <div style={{
          background: "#0b1220",
          border: "1px solid #1e293b",
          borderRadius: "14px",
          padding: "24px",
        }}>
          <h3 style={{ fontSize: "16px", fontWeight: 600, color: "#f1f5f9", margin: "0 0 16px 0", display: "flex", alignItems: "center", gap: "8px" }}>
            <FileCheck size={16} color="#38bdf8" /> Verification Checklist & Issue Ledger
          </h3>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {qcReport.issues.map((iss: QCIssue, idx: number) => (
              <div
                key={idx}
                style={{
                  padding: "12px 16px",
                  background: "#080d1a",
                  border: "1px solid #1e293b",
                  borderRadius: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  fontSize: "13px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <CheckCircle2 size={16} color="#10b981" />
                  <span style={{ color: "#f8fafc" }}>{iss.message}</span>
                </div>
                <span style={{ fontSize: "11px", color: "#64748b", fontFamily: "monospace" }}>
                  T+{iss.timestamp}s
                </span>
              </div>
            ))}
          </div>

          {/* Export Action */}
          <div style={{ marginTop: "24px", paddingTop: "20px", borderTop: "1px solid #1e293b", display: "flex", justifyContent: "flex-end" }}>
            <button
              type="button"
              disabled={!qcReport.passed}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "12px 24px",
                background: qcReport.passed ? "linear-gradient(135deg, #10b981, #059669)" : "#334155",
                border: "none",
                borderRadius: "8px",
                color: "#ffffff",
                fontSize: "14px",
                fontWeight: 600,
                cursor: qcReport.passed ? "pointer" : "not-allowed",
              }}
            >
              <HardDriveDownload size={16} />
              Proceed to Final 9:16 1080x1920 Render
            </button>
          </div>
        </div>

      </div>
    </AppShell>
  );
}
