"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../../components/app-shell";
import { ErrorState } from "../../../../components/domain-forms";
import { api, Episode, Subtitle, SubtitleCue } from "../../../../lib/api";
import { transcribeVideoWithCloudflare } from "../../../../lib/cloud-whisper";

const STYLE_PRESETS = [
  { id: "yellow_bold", name: "Yellow Punch", color: "#facc15", textShadow: "2px 2px 0px #000, -2px -2px 0px #000, 2px -2px 0px #000, -2px 2px 0px #000", bg: "transparent" },
  { id: "clean_white", name: "Clean White", color: "#ffffff", textShadow: "0 2px 4px rgba(0,0,0,0.8)", bg: "transparent" },
  { id: "neon_cyan", name: "Neon Cyan", color: "#38bdf8", textShadow: "0 0 8px rgba(56,189,248,0.8), 2px 2px 0px #000", bg: "transparent" },
  { id: "black_pill", name: "Classic Box", color: "#ffffff", textShadow: "none", bg: "rgba(0,0,0,0.75)" },
];

export default function SubtitleStudioPage({ params }: { params: { id: string } }) {
  const episodeId = params.id;
  const [episode, setEpisode] = useState<Episode | null>(null);
  const [subtitle, setSubtitle] = useState<Subtitle | null>(null);
  const [preset, setPreset] = useState("burmese_default");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [cloudFile, setCloudFile] = useState<File | null>(null);
  const [cloudProgress, setCloudProgress] = useState("");
  const [cloudUsage, setCloudUsage] = useState<{ audio_minutes: number; estimated_neurons: number; usage_ratio: number; warning: boolean; fallback_required: boolean } | null>(null);

  // Subtitle Styling & Player Sync State
  const [selectedStyle, setSelectedStyle] = useState("yellow_bold");
  const [previewCueIndex, setPreviewCueIndex] = useState(0);
  const [fontSize, setFontSize] = useState(20);

  async function load() {
    try {
      setError("");
      const [episodeItem, subtitles, usage] = await Promise.all([api.getEpisode(episodeId), api.listSubtitles(episodeId), api.getCloudWhisperUsage()]);
      setEpisode(episodeItem);
      const current = subtitles.find((item: Subtitle) => item.is_current) ?? subtitles[0] ?? null;
      setSubtitle(current);
      if (current) setPreset(current.preset);
      setCloudUsage(usage);
    } catch (e) { setError(e instanceof Error ? e.message : "Failed to load subtitle studio"); }
  }
  useEffect(() => { load(); }, [episodeId]);

  const errors = useMemo(() => subtitle?.validation_errors ?? [], [subtitle]);

  async function generate() {
    setBusy(true); setError("");
    try { const item = await api.generateSubtitle(episodeId, preset); setSubtitle(item); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to generate subtitles"); }
    finally { setBusy(false); }
  }

  function updateCue(index: number, patch: Partial<SubtitleCue>) {
    if (!subtitle) return;
    setSubtitle({ ...subtitle, cues: subtitle.cues.map((cue: SubtitleCue, i: number) => i === index ? { ...cue, ...patch } : cue) });
  }

  function nudgeTime(index: number, field: "start" | "end", delta: number) {
    if (!subtitle) return;
    const current = subtitle.cues[index][field];
    const updated = Math.max(0, Math.round((current + delta) * 10) / 10);
    updateCue(index, { [field]: updated });
  }

  function splitCue(index: number) {
    if (!subtitle) return;
    const cue = subtitle.cues[index];
    const mid = Math.round(((cue.start + cue.end) / 2) * 10) / 10;
    const words = cue.text.trim().split(/\s+/);
    const midWord = Math.ceil(words.length / 2);
    const text1 = words.slice(0, midWord).join(" ");
    const text2 = words.slice(midWord).join(" ");

    const cue1: SubtitleCue = { start: cue.start, end: mid, text: text1 || cue.text };
    const cue2: SubtitleCue = { start: mid, end: cue.end, text: text2 || "" };

    const newCues = [...subtitle.cues];
    newCues.splice(index, 1, cue1, cue2);
    setSubtitle({ ...subtitle, cues: newCues });
  }

  function mergeCue(index: number) {
    if (!subtitle || index >= subtitle.cues.length - 1) return;
    const cue1 = subtitle.cues[index];
    const cue2 = subtitle.cues[index + 1];
    const merged: SubtitleCue = {
      start: cue1.start,
      end: cue2.end,
      text: `${cue1.text} ${cue2.text}`.trim(),
    };
    const newCues = [...subtitle.cues];
    newCues.splice(index, 2, merged);
    setSubtitle({ ...subtitle, cues: newCues });
  }

  function addCueAfter(index: number) {
    if (!subtitle) return;
    const current = subtitle.cues[index];
    const newCue: SubtitleCue = {
      start: current ? Math.round((current.end + 0.1) * 10) / 10 : 0,
      end: current ? Math.round((current.end + 2.5) * 10) / 10 : 2.5,
      text: "",
    };
    const newCues = [...subtitle.cues];
    newCues.splice(index + 1, 0, newCue);
    setSubtitle({ ...subtitle, cues: newCues });
  }

  function deleteCue(index: number) {
    if (!subtitle) return;
    const newCues = subtitle.cues.filter((_, i) => i !== index);
    setSubtitle({ ...subtitle, cues: newCues });
  }

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        save();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [subtitle, preset]);

  async function save() {
    if (!subtitle) return;
    setBusy(true); setError("");
    try {
      const item = await api.updateSubtitle(subtitle.id, { cues: subtitle.cues, preset });
      setSubtitle(item);
    } catch (e) { setError(e instanceof Error ? e.message : "Failed to save subtitles"); }
    finally { setBusy(false); }
  }

  async function validate() {
    if (!subtitle) return;
    setBusy(true); setError("");
    try {
      await api.updateSubtitle(subtitle.id, { cues: subtitle.cues, preset });
      const result = await api.validateSubtitle(episodeId);
      setSubtitle({ ...subtitle, validation_errors: result.errors });
    } catch (e) { setError(e instanceof Error ? e.message : "Validation failed"); }
    finally { setBusy(false); }
  }

  async function approve() {
    if (!subtitle) return;
    setBusy(true); setError("");
    try { const item = await api.approveSubtitle(episodeId); setSubtitle(item); }
    catch (e) { setError(e instanceof Error ? e.message : "Subtitle approval failed"); }
    finally { setBusy(false); }
  }

  return <AppShell title="Subtitle Studio">
    <section className="card">
      <div className="eyebrow">BURMESE SUBTITLE QUALITY CONTROL</div>
      <h2>{episode?.public_id ?? "Episode"} · {episode?.title ?? "Loading..."}</h2>
      <p className="muted">Whisper transcript ကို editable cues အဖြစ်ပြောင်းပြီး timing/text quality gate ကို ဒီနေရာမှာ စစ်ပါ။ (Ctrl+S ဖြင့် သိမ်းဆည်းနိုင်ပါသည်)</p>
      {error && <ErrorState message={error} retry={load} />}
      <div className="inline-form">
        <select value={preset} onChange={e => setPreset(e.target.value)} aria-label="Subtitle preset">
          <option value="burmese_default">Burmese Default · 1–7s · 42 chars</option>
          <option value="burmese_compact">Burmese Compact · 1–5s · 32 chars</option>
        </select>
        <button className="primary" disabled={busy} onClick={generate}>Generate from transcript</button>
      </div>
    </section>
    
    <section className="card">
      <div className="eyebrow">CLOUDFLARE CLOUD PROCESSING</div>
      <h2>Browser FFmpeg → Cloudflare Whisper</h2>
      <p className="muted">Video ကို browser ထဲမှာ audio ပြောင်းပြီး Whisper ကို Cloudflare Workers AI ဆီပို့ပါတယ်။ Render server မှာ FFmpeg/Whisper မ run ပါဘူး။</p>
      {cloudUsage && <div className="muted">
        Today: {cloudUsage.audio_minutes.toFixed(1)} audio-min · ~{Math.round(cloudUsage.estimated_neurons)} neurons ({Math.round(cloudUsage.usage_ratio * 100)}% safety budget).
        {cloudUsage.fallback_required ? " Cloudflare safety budget reached — use Celery fallback." : cloudUsage.warning ? " 80% warning threshold reached." : ""}
      </div>}
      <div className="stack-form">
        <input type="file" accept="video/*" onChange={e => setCloudFile(e.target.files?.[0] ?? null)} aria-label="Choose video for Cloudflare transcription" />
        <div className="inline-form">
          <button className="primary" disabled={busy || !cloudFile} onClick={async () => {
            if (!cloudFile) return;
            setBusy(true); setError(""); setCloudProgress("");
            try {
              const result = await transcribeVideoWithCloudflare(
                episodeId,
                cloudFile,
                async (estimatedSeconds) => {
                  const token = await api.createCloudWhisperToken(episodeId, estimatedSeconds);
                  if (token.fallback_required) {
                    const job = await api.createRealJob(episodeId);
                    setCloudProgress(`Cloudflare daily safety threshold reached. Celery fallback queued (job ${job.id.slice(0, 8)}…).`);
                    throw new Error("__CLOUD_FALLBACK_QUEUED__");
                  }
                  return token;
                },
                setCloudProgress,
                (usageKey, audioSeconds) => api.recordCloudWhisperUsage(usageKey, audioSeconds),
              );
              const imported = await api.importCloudTranscript(episodeId, result.vtt, preset);
              setSubtitle(imported);
              setCloudProgress("Cloudflare transcript imported into Subtitle Studio.");
            } catch (e) {
              const message = e instanceof Error ? e.message : "Cloudflare transcription failed";
              if (message !== "__CLOUD_FALLBACK_QUEUED__") setError(message);
            } finally {
              setBusy(false);
            }
          }}>{busy ? "Processing…" : "Transcribe with Cloudflare"}</button>
          {cloudProgress && <span className="muted">{cloudProgress}</span>}
        </div>
      </div>
    </section>

    {!subtitle ? <section className="card"><div className="empty-state">No subtitle version yet. Run generation after processing creates a transcript.</div></section> :
      <>
        <section className="card">
          <div className="list-card"><div><strong>Version {subtitle.version}</strong><p className="muted">{subtitle.status} · {subtitle.cues.length} cues · {errors.length} validation issue(s)</p></div>
            <div className="inline-actions">
              <button className="text-button" disabled={busy} onClick={save}>Save</button>
              <button className="text-button" disabled={busy} onClick={validate}>Validate</button>
              <button className="primary" disabled={busy || errors.length > 0} onClick={approve}>Approve subtitle</button>
            </div>
          </div>
        </section>
        {errors.length > 0 && <section className="card"><div className="eyebrow">TIMING WARNINGS / QUALITY GATE</div><div className="list">{errors.map((item: Subtitle["validation_errors"][number], i: number) => <div className="list-card" key={i}><strong>{item.code}</strong><span className="muted">Cue {item.cue ?? "—"} · {item.message}</span></div>)}</div></section>}

        {/* 9:16 Video Player Sync & Subtitle Styling Preview */}
        <section className="card">
          <div className="eyebrow">9:16 LIVE SUBTITLE & VIDEO PLAYER PREVIEW</div>
          <h2>Interactive Styling & Audio Ducking Preview</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.5rem", marginTop: "1rem" }}>
            {/* 9:16 Mobile Canvas Simulation */}
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <div style={{
                width: "240px",
                height: "426px",
                borderRadius: "16px",
                border: "3px solid #334155",
                background: "linear-gradient(180deg, #090d16 0%, #1e1b4b 100%)",
                position: "relative",
                overflow: "hidden",
                boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.5)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                padding: "16px",
              }}>
                {/* Simulated Status */}
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "rgba(255,255,255,0.7)" }}>
                  <span>● LIVE</span>
                  <span>9:16 PORTRAIT</span>
                </div>

                {/* Subtitle Cue Overlay */}
                <div style={{
                  textAlign: "center",
                  padding: "8px 12px",
                  borderRadius: "8px",
                  background: STYLE_PRESETS.find(s => s.id === selectedStyle)?.bg,
                  marginBottom: "40px",
                }}>
                  <p className="burmese-text" style={{
                    color: STYLE_PRESETS.find(s => s.id === selectedStyle)?.color,
                    textShadow: STYLE_PRESETS.find(s => s.id === selectedStyle)?.textShadow,
                    fontSize: `${fontSize}px`,
                    fontWeight: 700,
                    margin: 0,
                    lineHeight: 1.6,
                  }}>
                    {subtitle.cues[previewCueIndex]?.text || "မြန်မာစာတန်းထိုး နမူနာ ကြည့်ရှုရန်"}
                  </p>
                </div>

                {/* Audio Ducking Indicator */}
                <div style={{ background: "rgba(0,0,0,0.6)", borderRadius: "6px", padding: "4px 8px", fontSize: "10px", color: "#10b981", display: "flex", justifyContent: "space-between" }}>
                  <span>🔊 Speech active</span>
                  <span>BGM ducked (-12dB)</span>
                </div>
              </div>
            </div>

            {/* Styling Controls */}
            <div className="stack-form">
              <div>
                <label style={{ display: "block", marginBottom: "0.4rem", fontSize: "0.875rem", fontWeight: 600 }}>Visual Style Preset</label>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "0.5rem" }}>
                  {STYLE_PRESETS.map(presetItem => (
                    <button
                      type="button"
                      key={presetItem.id}
                      onClick={() => setSelectedStyle(presetItem.id)}
                      className={selectedStyle === presetItem.id ? "primary" : "text-button"}
                      style={{ padding: "0.5rem", fontSize: "0.85rem", textAlign: "center" }}
                    >
                      {presetItem.name}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label style={{ display: "block", marginBottom: "0.4rem", fontSize: "0.875rem", fontWeight: 600 }}>Font Size ({fontSize}px)</label>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  {[18, 22, 26].map(size => (
                    <button
                      type="button"
                      key={size}
                      onClick={() => setFontSize(size)}
                      className={fontSize === size ? "primary" : "text-button"}
                      style={{ padding: "0.4rem 0.8rem", fontSize: "0.85rem" }}
                    >
                      {size === 18 ? "Small" : size === 22 ? "Medium" : "Large"} ({size}px)
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label style={{ display: "block", marginBottom: "0.4rem", fontSize: "0.875rem", fontWeight: 600 }}>Preview Cue (Jump to text)</label>
                <select
                  value={previewCueIndex}
                  onChange={e => setPreviewCueIndex(Number(e.target.value))}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #334155", background: "#0f172a", color: "#f8fafc" }}
                >
                  {subtitle.cues.map((c, idx) => (
                    <option key={idx} value={idx}>
                      #{idx + 1} ({c.start}s - {c.end}s): {c.text.slice(0, 30) || "Empty"}...
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </section>

        <section className="card">
          <div className="eyebrow">CUES ({subtitle.cues.length})</div>
          <div className="subtitle-cues" style={{ display: "grid", gap: "16px", marginTop: "12px" }}>
            {subtitle.cues.map((cue: SubtitleCue, index: number) =>
              <article className="card" key={cue.id ?? index} style={{ border: "1px solid var(--border)", padding: "14px", background: "var(--surface2)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <div className="eyebrow" style={{ padding: 0 }}>CUE #{index + 1}</div>
                  <div className="inline-actions" style={{ gap: "6px" }}>
                    <button type="button" className="text-button" onClick={() => splitCue(index)} title="Split cue into two parts">Split</button>
                    {index < subtitle.cues.length - 1 && (
                      <button type="button" className="text-button" onClick={() => mergeCue(index)} title="Merge with next cue">Merge Next</button>
                    )}
                    <button type="button" className="text-button" onClick={() => addCueAfter(index)} title="Insert new cue after this">+ Add</button>
                    <button type="button" className="text-button" style={{ color: "var(--danger)" }} onClick={() => deleteCue(index)} title="Delete this cue">Delete</button>
                  </div>
                </div>

                <div className="cue-fields ds-stack" style={{ gap: "10px" }}>
                  <div className="ds-row" style={{ gap: "14px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap" }}>
                      <label style={{ fontSize: "12px", color: "var(--muted)" }}>Start (s):</label>
                      <input
                        type="number"
                        min="0"
                        step="0.1"
                        style={{ width: "80px" }}
                        value={cue.start}
                        onChange={e => updateCue(index, { start: Number(e.target.value) })}
                      />
                      <button type="button" className="text-button" style={{ padding: "2px 6px" }} onClick={() => nudgeTime(index, "start", -0.5)}>-0.5s</button>
                      <button type="button" className="text-button" style={{ padding: "2px 6px" }} onClick={() => nudgeTime(index, "start", -0.1)}>-0.1s</button>
                      <button type="button" className="text-button" style={{ padding: "2px 6px" }} onClick={() => nudgeTime(index, "start", 0.1)}>+0.1s</button>
                      <button type="button" className="text-button" style={{ padding: "2px 6px" }} onClick={() => nudgeTime(index, "start", 0.5)}>+0.5s</button>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap" }}>
                      <label style={{ fontSize: "12px", color: "var(--muted)" }}>End (s):</label>
                      <input
                        type="number"
                        min="0"
                        step="0.1"
                        style={{ width: "80px" }}
                        value={cue.end}
                        onChange={e => updateCue(index, { end: Number(e.target.value) })}
                      />
                      <button type="button" className="text-button" style={{ padding: "2px 6px" }} onClick={() => nudgeTime(index, "end", -0.5)}>-0.5s</button>
                      <button type="button" className="text-button" style={{ padding: "2px 6px" }} onClick={() => nudgeTime(index, "end", -0.1)}>-0.1s</button>
                      <button type="button" className="text-button" style={{ padding: "2px 6px" }} onClick={() => nudgeTime(index, "end", 0.1)}>+0.1s</button>
                      <button type="button" className="text-button" style={{ padding: "2px 6px" }} onClick={() => nudgeTime(index, "end", 0.5)}>+0.5s</button>
                    </div>
                  </div>

                  <div>
                    <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "4px" }}>မြန်မာစာ စာတန်းထိုး (Burmese text)</label>
                    <textarea
                      className="burmese-text"
                      value={cue.text}
                      onChange={e => updateCue(index, { text: e.target.value })}
                      rows={2}
                      style={{ width: "100%", fontSize: "15px" }}
                    />
                  </div>
                </div>
              </article>
            )}
          </div>
        </section>
        <section className="card">
          <div className="eyebrow">EXPORT</div>
          <p className="muted">Approved or draft subtitle version ကို SRT/VTT အဖြစ် export/download လုပ်နိုင်ပါတယ်။</p>
          <div className="inline-actions">
            <a className="text-button" href={api.exportSubtitle(subtitle.id, "srt")} target="_blank" rel="noreferrer">SRT</a>
            <a className="text-button" href={api.exportSubtitle(subtitle.id, "vtt")} target="_blank" rel="noreferrer">VTT</a>
          </div>
        </section>
      </>}
  </AppShell>;
}
