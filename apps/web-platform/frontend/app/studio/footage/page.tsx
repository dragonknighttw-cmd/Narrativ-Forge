"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../../components/app-shell";
import { api } from "../../../lib/api";
import {
  FolderOpen,
  Film,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Play,
  Star,
  Tag,
  Video,
  Plus,
  Sliders,
  Filter,
} from "lucide-react";

interface RawFootageItem {
  id: string;
  filename: string;
  file_url: string;
  duration_seconds: number;
  resolution: string;
  quality_score: number;
  stability_score: number;
  camera_movement: string;
  selected_highlight: boolean;
  tags: string[];
  scenes: Array<{
    scene_id: string;
    start_time: number;
    end_time: number;
    duration: number;
    shot_type: string;
    camera_movement: string;
    is_highlight: boolean;
  }>;
  created_at: string;
}

const SAMPLE_FOOTAGES: RawFootageItem[] = [
  {
    id: "foot-1",
    filename: "cyber_detective_alleyway_walk.mp4",
    file_url: "https://example.com/footage-alley.mp4",
    duration_seconds: 18.5,
    resolution: "1080x1920 (9:16)",
    quality_score: 94.0,
    stability_score: 91.5,
    camera_movement: "Smooth Gimbal Tracking",
    selected_highlight: true,
    tags: ["protagonist", "b-roll", "rain-neon", "alley", "atmospheric"],
    scenes: [
      { scene_id: "s1", start_time: 0.0, end_time: 4.5, duration: 4.5, shot_type: "Wide Establishing Shot", camera_movement: "Slow Forward Track", is_highlight: false },
      { scene_id: "s2", start_time: 4.5, end_time: 9.0, duration: 4.5, shot_type: "Intense Close-Up", camera_movement: "Smooth Gimbal Pan", is_highlight: true },
      { scene_id: "s3", start_time: 9.0, end_time: 14.0, duration: 5.0, shot_type: "Low-Angle Hero Shot", camera_movement: "Handheld Subtle Shake", is_highlight: true },
      { scene_id: "s4", start_time: 14.0, end_time: 18.5, duration: 4.5, shot_type: "Over-Shoulder Follow", camera_movement: "Smooth Tracking", is_highlight: false },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: "foot-2",
    filename: "flying_drone_city_skyline_night.mp4",
    file_url: "https://example.com/footage-drone.mp4",
    duration_seconds: 24.0,
    resolution: "3840x2160 (4K UHD)",
    quality_score: 98.0,
    stability_score: 99.0,
    camera_movement: "Drone Aerial Sweeping Pan",
    selected_highlight: true,
    tags: ["landscape", "aerial", "skyline", "epic-scale"],
    scenes: [
      { scene_id: "s1", start_time: 0.0, end_time: 8.0, duration: 8.0, shot_type: "Extreme Wide Aerial", camera_movement: "Sweeping Flight", is_highlight: true },
      { scene_id: "s2", start_time: 8.0, end_time: 16.0, duration: 8.0, shot_type: "Top-Down Traffic Flow", camera_movement: "Forward Glide", is_highlight: false },
      { scene_id: "s3", start_time: 16.0, end_time: 24.0, duration: 8.0, shot_type: "Tower Reveal Shot", camera_movement: "Ascending Tilt", is_highlight: true },
    ],
    created_at: new Date(Date.now() - 3600000 * 4).toISOString(),
  },
];

export default function RawFootageHubPage() {
  const [footages, setFootages] = useState<RawFootageItem[]>(SAMPLE_FOOTAGES);
  const [highlightsOnly, setHighlightsOnly] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [filename, setFilename] = useState("");
  const [fileUrl, setFileUrl] = useState("");
  const [duration, setDuration] = useState("20");

  useEffect(() => {
    async function load() {
      try {
        const data = await api.listFootages(highlightsOnly);
        if (data && data.length > 0) setFootages(data);
      } catch {
        // Fallback smooth preview
      }
    }
    load();
  }, [highlightsOnly]);

  async function handleScan(e: React.FormEvent) {
    e.preventDefault();
    if (!filename || !fileUrl) return;
    setScanning(true);
    try {
      const res = await api.scanFootage({
        filename,
        file_url: fileUrl,
        duration_seconds: parseFloat(duration) || 20,
        resolution: "1080x1920 (9:16)",
      });
      if (res?.scanned_data) {
        const newItem: RawFootageItem = {
          id: res.id,
          filename: res.filename,
          file_url: fileUrl,
          duration_seconds: res.scanned_data.duration_seconds,
          resolution: res.scanned_data.resolution,
          quality_score: res.scanned_data.quality_score,
          stability_score: res.scanned_data.stability_score,
          camera_movement: res.scanned_data.camera_movement,
          selected_highlight: res.scanned_data.selected_highlight,
          tags: res.scanned_data.tags,
          scenes: res.scanned_data.scenes,
          created_at: new Date().toISOString(),
        };
        setFootages([newItem, ...footages]);
        setFilename("");
        setFileUrl("");
      }
    } catch {
      // Local fallback
      const fallbackItem: RawFootageItem = {
        id: `foot-${Date.now()}`,
        filename,
        file_url: fileUrl,
        duration_seconds: parseFloat(duration) || 20,
        resolution: "1080x1920",
        quality_score: 91.0,
        stability_score: 87.0,
        camera_movement: "Dynamic Gimbal Tracking",
        selected_highlight: true,
        tags: ["b-roll", "protagonist", "action"],
        scenes: [
          { scene_id: "s1", start_time: 0, end_time: 5, duration: 5, shot_type: "Establishing Shot", camera_movement: "Pan", is_highlight: false },
          { scene_id: "s2", start_time: 5, end_time: 12, duration: 7, shot_type: "Close-Up Hero", camera_movement: "Track", is_highlight: true },
        ],
        created_at: new Date().toISOString(),
      };
      setFootages([fallbackItem, ...footages]);
      setFilename("");
      setFileUrl("");
    } finally {
      setScanning(false);
    }
  }

  const displayedFootages = highlightsOnly
    ? footages.filter((f) => f.selected_highlight)
    : footages;

  return (
    <AppShell title="Raw Footage Intelligence Hub">
      <div style={{ display: "flex", flexDirection: "column", gap: "24px", paddingBottom: "48px" }}>
        
        {/* Header Intro */}
        <div style={{
          background: "#0b1220",
          border: "1px solid #1e293b",
          borderRadius: "14px",
          padding: "24px",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#10b981", fontSize: "12px", fontWeight: 700, letterSpacing: "0.05em", marginBottom: "6px" }}>
            <FolderOpen size={14} /> MODULE 02 · RAW FOOTAGE INTELLIGENCE
          </div>
          <h2 style={{ fontSize: "22px", fontWeight: 700, color: "#f8fafc", margin: "0 0 6px 0" }}>
            AI Automated Scene Detection & Best Shot Selection
          </h2>
          <p style={{ fontSize: "14px", color: "#94a3b8", margin: 0, maxWidth: "720px", lineHeight: "1.5" }}>
            ရိုက်ကူးထားသော Raw Video ဖိုင်များကို တင်လိုက်သည်နှင့် AI က လှုပ်ခါနေသော frame များနှင့် အသုံးမလိုသောအပိုင်းများကို ဖယ်ထုတ်ပေးပြီး
            အကောင်းဆုံး Highlights များနှင့် B-Roll Scene များကို အလိုအလျောက် ရွေးထုတ် Tagging တပ်ပေးပါမည်။
          </p>
        </div>

        {/* Scan Input Drawer */}
        <div style={{
          background: "#0b1220",
          border: "1px solid #1e293b",
          borderRadius: "14px",
          padding: "20px 24px",
        }}>
          <form onSubmit={handleScan} style={{ display: "grid", gridTemplateColumns: "1.2fr 1.5fr 120px auto", gap: "12px", alignItems: "end" }}>
            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "#94a3b8", marginBottom: "6px" }}>
                Footage Filename
              </label>
              <input
                type="text"
                required
                placeholder="e.g. hero_night_run_raw.mp4"
                value={filename}
                onChange={(e) => setFilename(e.target.value)}
                style={{
                  width: "100%",
                  background: "#080d1a",
                  border: "1px solid #1e293b",
                  borderRadius: "8px",
                  padding: "10px 14px",
                  color: "#f8fafc",
                  fontSize: "13.5px",
                  outline: "none",
                }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "#94a3b8", marginBottom: "6px" }}>
                File URL / Cloud Storage Path
              </label>
              <input
                type="url"
                required
                placeholder="https://example.com/raw-clip.mp4"
                value={fileUrl}
                onChange={(e) => setFileUrl(e.target.value)}
                style={{
                  width: "100%",
                  background: "#080d1a",
                  border: "1px solid #1e293b",
                  borderRadius: "8px",
                  padding: "10px 14px",
                  color: "#f8fafc",
                  fontSize: "13.5px",
                  outline: "none",
                }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "#94a3b8", marginBottom: "6px" }}>
                Secs
              </label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                style={{
                  width: "100%",
                  background: "#080d1a",
                  border: "1px solid #1e293b",
                  borderRadius: "8px",
                  padding: "10px 14px",
                  color: "#f8fafc",
                  fontSize: "13.5px",
                  outline: "none",
                }}
              />
            </div>

            <button
              type="submit"
              disabled={scanning}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "10px 18px",
                background: "linear-gradient(135deg, #059669, #047857)",
                border: "none",
                borderRadius: "8px",
                color: "#ffffff",
                fontSize: "13.5px",
                fontWeight: 600,
                cursor: scanning ? "not-allowed" : "pointer",
                height: "41px",
              }}
            >
              <Sparkles size={15} />
              {scanning ? "Scanning..." : "Scan Footage"}
            </button>
          </form>
        </div>

        {/* Filter Controls */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              type="button"
              onClick={() => setHighlightsOnly(false)}
              style={{
                padding: "6px 14px",
                borderRadius: "20px",
                fontSize: "12.5px",
                fontWeight: 600,
                border: "1px solid",
                borderColor: !highlightsOnly ? "#10b981" : "#1e293b",
                background: !highlightsOnly ? "rgba(16, 185, 129, 0.15)" : "#0b1220",
                color: !highlightsOnly ? "#34d399" : "#94a3b8",
                cursor: "pointer",
              }}
            >
              All Clips ({footages.length})
            </button>
            <button
              type="button"
              onClick={() => setHighlightsOnly(true)}
              style={{
                padding: "6px 14px",
                borderRadius: "20px",
                fontSize: "12.5px",
                fontWeight: 600,
                border: "1px solid",
                borderColor: highlightsOnly ? "#f59e0b" : "#1e293b",
                background: highlightsOnly ? "rgba(245, 158, 11, 0.15)" : "#0b1220",
                color: highlightsOnly ? "#fbbf24" : "#94a3b8",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              <Star size={13} />
              AI Best Highlights Only ({footages.filter((f) => f.selected_highlight).length})
            </button>
          </div>
        </div>

        {/* Footages Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: "20px" }}>
          {displayedFootages.map((f) => (
            <div
              key={f.id}
              style={{
                background: "#0b1220",
                border: "1px solid #1e293b",
                borderRadius: "14px",
                padding: "20px",
                display: "flex",
                flexDirection: "column",
                gap: "14px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <h4 style={{ fontSize: "15px", fontWeight: 600, color: "#f8fafc", margin: "0 0 4px 0" }}>
                    {f.filename}
                  </h4>
                  <div style={{ fontSize: "12px", color: "#64748b" }}>
                    {f.duration_seconds}s • {f.resolution} • {f.camera_movement}
                  </div>
                </div>
                {f.selected_highlight && (
                  <span style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    padding: "3px 8px",
                    borderRadius: "6px",
                    background: "rgba(245, 158, 11, 0.15)",
                    border: "1px solid rgba(245, 158, 11, 0.3)",
                    color: "#fbbf24",
                    fontSize: "11px",
                    fontWeight: 600,
                  }}>
                    <Star size={12} fill="#fbbf24" /> Best Highlight
                  </span>
                )}
              </div>

              {/* Quality Meters */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", background: "#080d1a", padding: "10px 14px", borderRadius: "8px" }}>
                <div>
                  <div style={{ fontSize: "10.5px", color: "#64748b" }}>Quality Score</div>
                  <div style={{ fontSize: "14px", fontWeight: 700, color: "#10b981", marginTop: "2px" }}>
                    {f.quality_score}%
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: "10.5px", color: "#64748b" }}>Stability Index</div>
                  <div style={{ fontSize: "14px", fontWeight: 700, color: "#38bdf8", marginTop: "2px" }}>
                    {f.stability_score}%
                  </div>
                </div>
              </div>

              {/* Detected Sub-Scenes List */}
              <div>
                <div style={{ fontSize: "11.5px", fontWeight: 700, color: "#64748b", textTransform: "uppercase", marginBottom: "8px" }}>
                  Detected Shot Slices ({f.scenes.length})
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                  {f.scenes.map((s) => (
                    <div
                      key={s.scene_id}
                      style={{
                        padding: "8px 10px",
                        background: s.is_highlight ? "rgba(245, 158, 11, 0.08)" : "#080d1a",
                        border: `1px solid ${s.is_highlight ? "rgba(245, 158, 11, 0.25)" : "#1e293b"}`,
                        borderRadius: "6px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        fontSize: "12px",
                      }}
                    >
                      <span style={{ color: "#f1f5f9", fontWeight: 500 }}>
                        {s.start_time}s – {s.end_time}s: {s.shot_type}
                      </span>
                      {s.is_highlight && (
                        <span style={{ fontSize: "10px", color: "#fbbf24", fontWeight: 700, display: "inline-flex", alignItems: "center", gap: "3px" }}>
                          <Star size={11} fill="currentColor" /> Highlight
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Tags */}
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "auto" }}>
                {f.tags.map((t) => (
                  <span key={t} style={{
                    fontSize: "10.5px",
                    padding: "2px 8px",
                    borderRadius: "4px",
                    background: "rgba(255, 255, 255, 0.05)",
                    color: "#94a3b8",
                  }}>
                    #{t}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

      </div>
    </AppShell>
  );
}
