"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../../components/app-shell";
import { api } from "../../../lib/api";
import {
  Clapperboard,
  Sparkles,
  CheckCircle2,
  TrendingUp,
  Sliders,
  Play,
  ArrowRight,
  Flame,
  Zap,
  Heart,
  Music,
} from "lucide-react";

interface ConceptItem {
  id: string;
  concept_type: string;
  title: string;
  logline: string;
  target_duration_seconds: number;
  pacing_profile: string;
  recommended_bgm_genre: string;
  emotional_arc: Array<{ time: string; emotion: string; intensity: number }>;
  shot_decisions: string[];
  status: string;
}

const SAMPLE_CONCEPTS: ConceptItem[] = [
  {
    id: "concept-1",
    concept_type: "epic_cinematic",
    title: "Epic Cinematic Cut: Yangon Shadow Protocol",
    logline: "Grand orchestral scale with dramatic slow-motion reveals, deep volumetric teal-amber grading, and thunderous war drums.",
    target_duration_seconds: 180,
    pacing_profile: "Majestic & Deliberate (3.5s - 5.0s / cut)",
    recommended_bgm_genre: "Two Steps From Hell / Battle Orchestral",
    emotional_arc: [
      { time: "0:00", emotion: "Mysterious Awe", intensity: 45 },
      { time: "0:45", emotion: "Mounting Suspense", intensity: 72 },
      { time: "1:30", emotion: "Climactic Confrontation", intensity: 98 },
      { time: "2:45", emotion: "Lingering Cliffhanger", intensity: 85 },
    ],
    shot_decisions: [
      "Open with extreme wide drone shot to establish massive urban cityscape.",
      "Slow push-in on protagonist eyes during narrative revelation at 0:45.",
      "Rapid cut montage synchronized to war drum drops between 1:20 and 1:50.",
      "Hold final 4 seconds on solitary silhouette before fading to title card.",
    ],
    status: "approved",
  },
  {
    id: "concept-2",
    concept_type: "fast_paced_social",
    title: "Viral 9:16 Social Cut: Yangon Shadow Protocol",
    logline: "Aggressive 2.0-second cuts optimized for TikTok & Reels retention with instant 0.5s visual hook and phonk bass drops.",
    target_duration_seconds: 90,
    pacing_profile: "Rapid Fire (1.8s - 2.4s / cut)",
    recommended_bgm_genre: "Phonk / Dark Electronic Pulse",
    emotional_arc: [
      { time: "0:00", emotion: "Shock Hook", intensity: 95 },
      { time: "0:15", emotion: "Rapid Escalation", intensity: 88 },
      { time: "0:45", emotion: "Mind-Bending Climax", intensity: 100 },
      { time: "1:15", emotion: "Viral CTA & Share Hook", intensity: 90 },
    ],
    shot_decisions: [
      "Pattern-interrupt shock cut within the first 0.6 seconds to stop scrolling.",
      "Dynamic zoom-ins on key action moments with speed-ramping.",
      "Bold kinetic neon Burmese typography centered in safe viewing zone.",
      "End with open loop question to drive comment section debates.",
    ],
    status: "draft",
  },
  {
    id: "concept-3",
    concept_type: "emotional_storytelling",
    title: "Intimate Narrative Cut: Yangon Shadow Protocol",
    logline: "Poignant character-driven pacing focusing on micro-expressions, ambient silence, and soft piano chords.",
    target_duration_seconds: 180,
    pacing_profile: "Contemplative & Intimate (4.0s - 6.5s / cut)",
    recommended_bgm_genre: "Dramatic Piano & Cello Solo",
    emotional_arc: [
      { time: "0:00", emotion: "Vulnerable Nostalgia", intensity: 35 },
      { time: "1:00", emotion: "Quiet Realization", intensity: 60 },
      { time: "2:00", emotion: "Heartbreaking Climax", intensity: 92 },
      { time: "2:50", emotion: "Cathartic Solitude", intensity: 65 },
    ],
    shot_decisions: [
      "Prioritize handheld breathing camera movements over rigid locked shots.",
      "Allow dialogue pauses to breathe against subtle ambient environmental room tone.",
      "Gradual color temperature shift from cold teal to warm gold across the narrative arc.",
    ],
    status: "draft",
  },
];

export default function CreativeDirectorPage() {
  const [concepts, setConcepts] = useState<ConceptItem[]>(SAMPLE_CONCEPTS);
  const [selectedConcept, setSelectedConcept] = useState<ConceptItem>(SAMPLE_CONCEPTS[0]);
  const [episodeTitle, setEpisodeTitle] = useState("");
  const [logline, setLogline] = useState("");
  const [targetDuration, setTargetDuration] = useState("180");
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.listConcepts();
        if (data && data.length > 0) {
          setConcepts(data);
          setSelectedConcept(data[0]);
        }
      } catch {
        // Fallback smooth preview
      }
    }
    load();
  }, []);

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    if (!episodeTitle || !logline) return;
    setGenerating(true);
    try {
      const res = await api.generateConcepts({
        episode_title: episodeTitle,
        logline,
        target_duration_seconds: parseInt(targetDuration) || 180,
      });
      if (res && res.length > 0) {
        setConcepts(res);
        setSelectedConcept(res[0]);
        setEpisodeTitle("");
        setLogline("");
      }
    } catch {
      // Local fallback
    } finally {
      setGenerating(false);
    }
  }

  const getConceptIcon = (type: string) => {
    if (type === "epic_cinematic") return <Flame size={16} color="#f59e0b" />;
    if (type === "fast_paced_social") return <Zap size={16} color="#38bdf8" />;
    return <Heart size={16} color="#ec4899" />;
  };

  return (
    <AppShell title="AI Creative Director Engine">
      <div style={{ display: "flex", flexDirection: "column", gap: "24px", paddingBottom: "48px" }}>
        
        {/* Intro */}
        <div style={{
          background: "#0b1220",
          border: "1px solid #1e293b",
          borderRadius: "14px",
          padding: "24px",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#f59e0b", fontSize: "12px", fontWeight: 700, letterSpacing: "0.05em", marginBottom: "6px" }}>
            <Clapperboard size={14} /> MODULE 03 · AI CREATIVE DIRECTOR
          </div>
          <h2 style={{ fontSize: "22px", fontWeight: 700, color: "#f8fafc", margin: "0 0 6px 0" }}>
            Intelligent Storytelling & Multi-Concept Editing Synthesis
          </h2>
          <p style={{ fontSize: "14px", color: "#94a3b8", margin: 0, maxWidth: "750px", lineHeight: "1.5" }}>
            AI Director သည် ဗီဒီယိုကို ရိုးရိုးဖြတ်ဆက်ရုံသာမက ဘယ်လိုတည်းဖြတ်လျှင် ပိုကောင်းမည်ကို ဒါရိုက်တာတစ်ဦးကဲ့သို့ ဆုံးဖြတ်ပေးပါသည်။
            ရိုက်ချက်တစ်ခုချင်းစီအတွက် မည်သည့်အတွက်ကြောင့် ရွေးချယ်ထားကြောင်း (Shot Decisions) ကို တိုက်ရိုက်ရှင်းပြပြီး
            Concept (၃) မျိုး (Epic, 9:16 Social, Emotional) အနက်မှ စိတ်ကြိုက် ရွေးချယ်နိုင်ပါသည်။
          </p>
        </div>

        {/* Form Drawer */}
        <div style={{
          background: "#0b1220",
          border: "1px solid #1e293b",
          borderRadius: "14px",
          padding: "20px 24px",
        }}>
          <form onSubmit={handleGenerate} style={{ display: "grid", gridTemplateColumns: "1fr 1.6fr 130px auto", gap: "12px", alignItems: "end" }}>
            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "#94a3b8", marginBottom: "6px" }}>
                Episode Title
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Episode 04: The Final Revelation"
                value={episodeTitle}
                onChange={(e) => setEpisodeTitle(e.target.value)}
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
                Story Synopsis / Logline
              </label>
              <input
                type="text"
                required
                placeholder="A rogue AI awakens in Yangon and leaves a cryptic warning..."
                value={logline}
                onChange={(e) => setLogline(e.target.value)}
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
                Duration (Secs)
              </label>
              <input
                type="number"
                value={targetDuration}
                onChange={(e) => setTargetDuration(e.target.value)}
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
              disabled={generating}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "10px 18px",
                background: "linear-gradient(135deg, #d97706, #b45309)",
                border: "none",
                borderRadius: "8px",
                color: "#ffffff",
                fontSize: "13.5px",
                fontWeight: 600,
                cursor: generating ? "not-allowed" : "pointer",
                height: "41px",
              }}
            >
              <Sparkles size={15} />
              {generating ? "Synthesizing..." : "Generate 3 Concepts"}
            </button>
          </form>
        </div>

        {/* 3 Concept Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "18px" }}>
          {concepts.map((c) => {
            const isSelected = selectedConcept?.id === c.id;
            return (
              <div
                key={c.id}
                onClick={() => setSelectedConcept(c)}
                style={{
                  background: isSelected ? "rgba(245, 158, 11, 0.08)" : "#0b1220",
                  border: `2px solid ${isSelected ? "#f59e0b" : "#1e293b"}`,
                  borderRadius: "14px",
                  padding: "20px",
                  cursor: "pointer",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  transition: "all 0.2s ease",
                }}
              >
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", fontWeight: 700, color: "#f59e0b", textTransform: "uppercase" }}>
                      {getConceptIcon(c.concept_type)}
                      {c.concept_type.replace(/_/g, " ")}
                    </div>
                    {isSelected && (
                      <span style={{ fontSize: "11px", fontWeight: 700, color: "#10b981", display: "flex", alignItems: "center", gap: "3px" }}>
                        <CheckCircle2 size={13} /> ACTIVE
                      </span>
                    )}
                  </div>

                  <h3 style={{ fontSize: "16.5px", fontWeight: 700, color: "#f8fafc", margin: "0 0 8px 0" }}>
                    {c.title}
                  </h3>
                  <p style={{ fontSize: "13px", color: "#94a3b8", lineHeight: "1.5", margin: "0 0 14px 0" }}>
                    {c.logline}
                  </p>
                </div>

                <div style={{ borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "12px", display: "flex", flexDirection: "column", gap: "6px" }}>
                  <div style={{ fontSize: "11.5px", color: "#64748b" }}>
                    ⏱ Pacing: <span style={{ color: "#f1f5f9" }}>{c.pacing_profile}</span>
                  </div>
                  <div style={{ fontSize: "11.5px", color: "#64748b" }}>
                    🎵 Score: <span style={{ color: "#38bdf8" }}>{c.recommended_bgm_genre}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Detailed Concept Inspector */}
        {selectedConcept && (
          <div style={{
            background: "#0b1220",
            border: "1px solid #1e293b",
            borderRadius: "14px",
            padding: "24px",
            display: "grid",
            gridTemplateColumns: "1.2fr 1fr",
            gap: "28px",
          }}>
            
            {/* Left: Shot Decisions (Why AI chose these shots) */}
            <div>
              <div style={{ fontSize: "12px", fontWeight: 700, color: "#38bdf8", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "8px" }}>
                AI Director • Shot Selection Decisions
              </div>
              <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#f8fafc", margin: "0 0 14px 0" }}>
                Cinematic Justifications & Cut Sequence
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {selectedConcept.shot_decisions.map((decision, i) => (
                  <div
                    key={i}
                    style={{
                      padding: "12px 14px",
                      background: "#080d1a",
                      border: "1px solid #1e293b",
                      borderRadius: "8px",
                      fontSize: "13px",
                      color: "#e2e8f0",
                      lineHeight: "1.5",
                      display: "flex",
                      gap: "10px",
                    }}
                  >
                    <span style={{ fontSize: "12px", fontWeight: 700, color: "#f59e0b", minWidth: "20px" }}>
                      #{i + 1}
                    </span>
                    <span>{decision}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Emotional Tension Arc */}
            <div>
              <div style={{ fontSize: "12px", fontWeight: 700, color: "#ec4899", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "8px" }}>
                Emotional Arc & Dynamic Pacing Curve
              </div>
              <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#f8fafc", margin: "0 0 14px 0" }}>
                Narrative Intensity Timeline
              </h3>

              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {selectedConcept.emotional_arc.map((arc, i) => (
                  <div key={i}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px", marginBottom: "4px" }}>
                      <span style={{ fontWeight: 600, color: "#f1f5f9" }}>{arc.time} — {arc.emotion}</span>
                      <span style={{ color: "#ec4899", fontWeight: 700 }}>{arc.intensity}%</span>
                    </div>
                    <div style={{ height: "6px", background: "#080d1a", borderRadius: "3px", overflow: "hidden" }}>
                      <div style={{
                        height: "100%",
                        width: `${arc.intensity}%`,
                        background: "linear-gradient(90deg, #ec4899, #f59e0b)",
                        borderRadius: "3px",
                      }} />
                    </div>
                  </div>
                ))}
              </div>

              {/* Apply Action */}
              <button
                type="button"
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  padding: "12px",
                  background: "linear-gradient(135deg, #10b981, #059669)",
                  border: "none",
                  borderRadius: "8px",
                  color: "#ffffff",
                  fontWeight: 600,
                  fontSize: "14px",
                  cursor: "pointer",
                  marginTop: "28px",
                  boxShadow: "0 4px 12px rgba(16, 185, 129, 0.3)",
                }}
              >
                <CheckCircle2 size={16} />
                Apply Concept to Multi-Track Timeline
              </button>
            </div>

          </div>
        )}

      </div>
    </AppShell>
  );
}
