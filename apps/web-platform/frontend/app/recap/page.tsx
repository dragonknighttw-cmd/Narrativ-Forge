"use client";

import { useState } from "react";
import { AppShell } from "../../components/app-shell";
import { api, RecapEditSimulation, RecapScript } from "../../lib/api";

const TEMPLATES = [
  {
    id: "thriller_suspense",
    name: "Thriller & Suspense",
    localName: "သည်းထိတ်ရင်ဖို",
    tone: "Suspenseful",
    hook: "Shocking twist",
    description: "လျှို့ဝှက်ချက်၊ သဲလွန်စနဲ့ အလှည့်အပြောင်းများကို အခြေခံတဲ့ ဇာတ်လမ်းပြောပုံ။",
  },
  {
    id: "action_blockbuster",
    name: "Action & Crime",
    localName: "အက်ရှင်နှင့် ရာဇဝတ်မှု",
    tone: "High energy",
    hook: "Explosive action",
    description: "အရှိန်မြန်တဲ့ အက်ရှင်ခန်းနဲ့ တင်းမာတဲ့ ဇာတ်လမ်းတင်ဆက်မှု။",
  },
  {
    id: "emotional_drama",
    name: "Emotional Drama",
    localName: "ရင်နင့်ဖွယ် ဒရာမာ",
    tone: "Emotional",
    hook: "Heartfelt story",
    description: "မိသားစု၊ အချစ်နဲ့ လူနေမှုဘဝကို ညင်သာလေးနက်စွာ ပြောပြခြင်း။",
  },
  {
    id: "sci_fi_mystery",
    name: "Sci-Fi & Mystery",
    localName: "သိပ္ပံစိတ်ကူးယဉ်",
    tone: "Mysterious",
    hook: "Paradox",
    description: "အချိန်၊ နည်းပညာနဲ့ စကြာဝဠာဆိုင်ရာ ဆန်းကြယ်မှုများ။",
  },
] as const;

export default function MovieRecapStudio() {
  const [movieTitle, setMovieTitle] = useState("");
  const [synopsis, setSynopsis] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState<(typeof TEMPLATES)[number]["id"]>("thriller_suspense");
  const [duration, setDuration] = useState(90);
  const [aspectRatio, setAspectRatio] = useState("9:16");
  const [subtitleStyle, setSubtitleStyle] = useState("tiktok_yellow");
  const [scriptData, setScriptData] = useState<RecapScript | null>(null);
  const [simulation, setSimulation] = useState<RecapEditSimulation | null>(null);
  const [loading, setLoading] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function generateScript() {
    if (!movieTitle.trim()) {
      setError("Movie title is required.");
      return;
    }
    setLoading(true);
    setError("");
    setNotice("");
    setSimulation(null);
    try {
      const result = await api.generateRecapScript({
        title: movieTitle.trim(),
        synopsis: synopsis.trim(),
        template_id: selectedTemplate,
        duration_seconds: duration,
      });
      setScriptData(result);
      setNotice("Template-based Burmese script draft created. Review every scene before using it.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create the recap draft");
    } finally {
      setLoading(false);
    }
  }

  async function previewEditPlan() {
    if (!scriptData) return;
    setPreviewing(true);
    setError("");
    setNotice("");
    try {
      const result = await api.previewRecapEdit({
        recap_script: scriptData,
        aspect_ratio: aspectRatio,
        subtitle_style: subtitleStyle,
      });
      setSimulation(result);
      setNotice("Edit-plan simulation completed. No video file was rendered or exported.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to preview the edit plan");
    } finally {
      setPreviewing(false);
    }
  }

  return (
    <AppShell title="Movie Recap Studio">
      <section className="recap-hero">
        <div className="eyebrow">BURMESE STORY RECAP WORKSPACE</div>
        <h2>Shape the story before you cut the film.</h2>
        <p>ရုပ်ရှင်အမည်နဲ့ ဇာတ်လမ်းအကျဉ်းကို ထည့်ပြီး မြန်မာဇာတ်လမ်းပြော draft တစ်ခု ပြုလုပ်ပါ။ Scene တစ်ခုချင်းစီကို ပြန်စစ်ပြီးမှ နောက်ထပ် production workflow ဆီ ဆက်သွားပါ။</p>
        <div className="recap-capability-note"><span aria-hidden="true">i</span><span>လက်ရှိအဆင့်မှာ template-based script draft နဲ့ edit-plan simulation ကိုသာ ပံ့ပိုးထားပါတယ်။ Live AI inference, FFmpeg render, Whisper transcription, MP4 download နဲ့ Drive export မလုပ်ဆောင်သေးပါ။</span></div>
      </section>

      {error && <div className="error recap-error" role="alert"><span>{error}</span><button type="button" className="text-button" onClick={() => setError("")}>Dismiss</button></div>}
      {notice && <p className="dashboard-inline-success" role="status">{notice}</p>}

      <div className="recap-workspace">
        <div className="recap-main-column">
          <section className="card recap-section">
            <div className="recap-step-heading"><span>01</span><div><div className="eyebrow">STORY INPUT</div><h3>Movie & synopsis</h3></div></div>
            <div className="recap-form-grid">
              <label className="recap-field recap-field-full"><span>Movie title / ရုပ်ရှင်အမည်</span><input value={movieTitle} onChange={(event) => setMovieTitle(event.target.value)} maxLength={200} placeholder="ဥပမာ — Parasite (2019)" required /></label>
              <label className="recap-field recap-field-full"><span>Synopsis / source notes (reference only)</span><textarea value={synopsis} onChange={(event) => setSynopsis(event.target.value)} rows={5} maxLength={5000} placeholder="သင့်ကိုယ်ပိုင် reference notes ကို ဒီမှာ ထည့်နိုင်ပါတယ်…" /><small className="settings-note">လက်ရှိ template engine က movie title နဲ့ tone ကိုသာ အသုံးပြုပါတယ်။ Synopsis ကို အလိုအလျောက် အဓိပ္ပာယ်ဖော်ခြင်း မလုပ်သေးပါ။</small></label>
            </div>
            <div className="recap-field-label">Storytelling tone</div>
            <div className="recap-template-grid">
              {TEMPLATES.map((item) => (
                <button className={`recap-template-card${selectedTemplate === item.id ? " is-selected" : ""}`} type="button" key={item.id} aria-pressed={selectedTemplate === item.id} onClick={() => setSelectedTemplate(item.id)}>
                  <strong>{item.name}</strong><span>{item.localName}</span><small>{item.description}</small><em>{item.hook}</em>
                </button>
              ))}
            </div>
            <div className="recap-bottom-controls">
              <label className="recap-field"><span>Target duration</span><select value={duration} onChange={(event) => setDuration(Number(event.target.value))}><option value={60}>60 seconds</option><option value={90}>90 seconds</option><option value={180}>3 minutes</option><option value={300}>5 minutes</option></select></label>
              <button className="primary" type="button" onClick={generateScript} disabled={loading || !movieTitle.trim()}>{loading ? "Creating draft…" : "Create Burmese script draft"}</button>
            </div>
          </section>

          {scriptData && (
            <section className="card recap-section">
              <div className="recap-step-heading"><span>02</span><div><div className="eyebrow">SCRIPT DRAFT · HUMAN REVIEW REQUIRED</div><h3>{scriptData.title}</h3></div><span className="ds-badge">{scriptData.total_scenes} scenes</span></div>
              <div className="recap-script-summary"><span>{scriptData.template.name}</span><span>{scriptData.target_duration_seconds}s target</span><span>{scriptData.job_id}</span></div>
              <div className="recap-full-script"><div className="eyebrow">FULL NARRATION DRAFT</div><p className="burmese-text">{scriptData.full_script_burmese}</p></div>
              <div className="recap-scenes-list">
                {scriptData.scenes.map((scene) => (
                  <article className="recap-scene-card" key={scene.scene_number}>
                    <div className="recap-scene-meta"><strong>SCENE {scene.scene_number.toString().padStart(2,"0")}</strong><span>{scene.start_time} — {scene.end_time}</span><span>{scene.pacing}</span></div>
                    <p className="burmese-text">{scene.burmese_narration}</p>
                    <div className="recap-scene-direction"><span>VISUAL DIRECTION</span>{scene.visual_description}</div>
                    <div className="recap-scene-direction"><span>EDIT NOTE</span>{scene.action_required}</div>
                  </article>
                ))}
              </div>
            </section>
          )}
        </div>

        <aside className="recap-side-column">
          <section className="card recap-section recap-edit-settings">
            <div className="recap-step-heading"><span>03</span><div><div className="eyebrow">EDIT PLAN</div><h3>Preview settings</h3></div></div>
            <label className="recap-field"><span>Aspect ratio</span><select value={aspectRatio} onChange={(event) => setAspectRatio(event.target.value)}><option value="9:16">9:16 · Vertical</option><option value="16:9">16:9 · Landscape</option></select></label>
            <label className="recap-field"><span>Subtitle style</span><select value={subtitleStyle} onChange={(event) => setSubtitleStyle(event.target.value)}><option value="tiktok_yellow">Yellow pop</option><option value="cinema_white">Clean white</option><option value="neon_glow">Neon glow</option></select></label>
            <div className="recap-selected-template"><span>SELECTED TONE</span><strong>{template.name}</strong><small>{template.tone} · {template.hook}</small></div>
            <button className="primary recap-preview-button" type="button" onClick={previewEditPlan} disabled={!scriptData || previewing}>{previewing ? "Preparing preview…" : "Preview edit plan"}</button>
            <p className="settings-note">Simulation only. This action does not render media, consume provider inference quota, or send external messages.</p>
          </section>

          {simulation && (
            <section className="card recap-section recap-simulation-card">
              <div className="recap-step-heading"><span>04</span><div><div className="eyebrow">SIMULATION RESULT</div><h3>Edit plan prepared</h3></div></div>
              <span className="ds-badge">NO VIDEO RENDERED</span>
              <div className="recap-simulation-meta">
                <div><span>Plan reference</span><strong>{simulation.render_job_id}</strong></div>
                <div><span>Canvas</span><strong>{simulation.resolution} · {simulation.aspect_ratio}</strong></div>
                <div><span>Target duration</span><strong>{simulation.duration_seconds}s</strong></div>
                <div><span>Scenes in plan</span><strong>{simulation.scenes_processed.length}</strong></div>
              </div>
              <p className="recap-simulation-disclaimer">The backend currently returns an edit-plan simulation. No MP4 exists, so download and Google Drive export are intentionally unavailable.</p>
            </section>
          )}
        </aside>
      </div>
    </AppShell>
  );
}
