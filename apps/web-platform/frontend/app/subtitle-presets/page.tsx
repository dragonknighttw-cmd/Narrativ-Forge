"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "../../components/app-shell";

const presets = [
  {
    id: "burmese_default",
    name: "Burmese Default",
    tone: "Balanced readability",
    maxChars: 42,
    minSeconds: 1,
    maxSeconds: 7,
    description: "သဘာဝကျတဲ့ စကားပြောနှုန်းနဲ့ ပုံမှန် short-form video များအတွက်။",
    sample: "ဒီနေ့မှာ စိတ်ဝင်စားစရာ အကြောင်းအရာတစ်ခုကို ပြောပြပါမယ်။",
  },
  {
    id: "burmese_compact",
    name: "Burmese Compact",
    tone: "Fast-paced captions",
    maxChars: 32,
    minSeconds: 1,
    maxSeconds: 5,
    description: "မြန်ဆန်တဲ့ edit နဲ့ စာတန်းတိုတိုများအတွက်။",
    sample: "ဒီအကြောင်းကို သင် သိပြီးပြီလား။",
  },
] as const;

export default function SubtitlePresetsPage() {
  const [selected, setSelected] = useState<(typeof presets)[number]["id"]>("burmese_default");
  const active = presets.find((preset) => preset.id === selected) ?? presets[0];

  return (
    <AppShell title="Subtitle Presets">
      <div className="page-intro">
        <div className="eyebrow">BURMESE CAPTION SYSTEM</div>
        <h2>Choose the rhythm of your subtitles.</h2>
        <p className="muted">Presets define cue length and reading time. They are selected for each subtitle version in Subtitle Studio; this page does not silently change existing approved subtitles.</p>
      </div>

      <div className="subtitle-preset-grid">
        {presets.map((preset) => (
          <button
            className={`subtitle-preset-card${selected === preset.id ? " is-selected" : ""}`}
            key={preset.id}
            type="button"
            aria-pressed={selected === preset.id}
            onClick={() => setSelected(preset.id)}
          >
            <span className="subtitle-preset-check" aria-hidden="true">{selected === preset.id ? "✓" : " "}</span>
            <span className="eyebrow">{preset.id === "burmese_default" ? "STANDARD" : "COMPACT"}</span>
            <strong>{preset.name}</strong>
            <span className="subtitle-preset-tone">{preset.tone}</span>
            <span className="subtitle-preset-description">{preset.description}</span>
            <span className="subtitle-preset-specs">
              <span><b>{preset.maxChars}</b> chars max</span>
              <span><b>{preset.minSeconds}–{preset.maxSeconds}s</b> display time</span>
              <span><b>2</b> lines max</span>
            </span>
          </button>
        ))}
      </div>

      <section className="card subtitle-preset-preview">
        <div className="eyebrow">LIVE PREVIEW · {active.name.toUpperCase()}</div>
        <h3>Sample subtitle appearance</h3>
        <div className="subtitle-preview-stage">
          <div className="subtitle-preview-safe-area">
            <span>9:16 · SAFE CAPTION AREA</span>
            <strong className="burmese-text">{active.sample}</strong>
          </div>
        </div>
        <div className="subtitle-preview-summary">
          <div><span>Maximum characters</span><strong>{active.maxChars}</strong></div>
          <div><span>Display duration</span><strong>{active.minSeconds}–{active.maxSeconds} sec</strong></div>
          <div><span>Maximum lines</span><strong>2</strong></div>
        </div>
        <p className="settings-note">Burmese text is normalized to Unicode NFC. Cues that exceed the selected preset's rules will be flagged by the subtitle quality gate.</p>
        <Link className="primary subtitle-preset-cta" href="/subtitles">Open Subtitle Studio <span aria-hidden="true">→</span></Link>
      </section>
    </AppShell>
  );
}
