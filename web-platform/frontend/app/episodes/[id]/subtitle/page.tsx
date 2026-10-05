"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../../components/app-shell";
import { ErrorState } from "../../../../components/domain-forms";
import { api, Episode, Subtitle, SubtitleCue } from "../../../../lib/api";
import { transcribeVideoWithCloudflare } from "../../../../lib/cloud-whisper";

export default function SubtitleStudioPage({ params }: { params: { id: string } }) {
  const episodeId = params.id;
  const [episode, setEpisode] = useState<Episode | null>(null);
  const [subtitle, setSubtitle] = useState<Subtitle | null>(null);
  const [preset, setPreset] = useState("burmese_default");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [cloudFile, setCloudFile] = useState<File | null>(null);
  const [cloudProgress, setCloudProgress] = useState("");

  async function load() {
    try {
      setError("");
      const [episodeItem, subtitles] = await Promise.all([api.getEpisode(episodeId), api.listSubtitles(episodeId)]);
      setEpisode(episodeItem);
      const current = subtitles.find((item: Subtitle) => item.is_current) ?? subtitles[0] ?? null;
      setSubtitle(current);
      if (current) setPreset(current.preset);
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
      <p className="muted">Whisper transcript ကို editable cues အဖြစ်ပြောင်းပြီး timing/text quality gate ကို ဒီနေရာမှာ စစ်ပါ။</p>
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
                (estimatedSeconds) => api.createCloudWhisperToken(episodeId, estimatedSeconds),
                setCloudProgress,
                (usageKey, audioSeconds) => api.recordCloudWhisperUsage(usageKey, audioSeconds),
              );
              const imported = await api.importCloudTranscript(episodeId, result.vtt, preset);
              setSubtitle(imported);
              setCloudProgress("Cloudflare transcript imported into Subtitle Studio.");
            } catch (e) {
              setError(e instanceof Error ? e.message : "Cloudflare transcription failed");
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
        <section className="card">
          <div className="eyebrow">CUES</div>
          <div className="subtitle-cues">{subtitle.cues.map((cue: SubtitleCue, index: number) =>
            <article className="subtitle-cue" key={cue.id ?? index}>
              <div className="cue-number">{index + 1}</div>
              <div className="cue-fields">
                <div className="cue-timing">
                  <label>Start<input type="number" min="0" step="0.1" value={cue.start} onChange={e => updateCue(index, { start: Number(e.target.value) })} /></label>
                  <label>End<input type="number" min="0" step="0.1" value={cue.end} onChange={e => updateCue(index, { end: Number(e.target.value) })} /></label>
                </div>
                <label>မြန်မာစာ<textarea value={cue.text} onChange={e => updateCue(index, { text: e.target.value })} rows={2} /></label>
              </div>
            </article>
          )}</div>
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
