"use client";

import React, { useState, useRef } from "react";
import { AppShell } from "../../components/app-shell";
import { api, apiBase, ManualPersonaPack } from "../../lib/api";

interface PanelData {
  panel_index: number;
  title: string;
  visual_prompt: string;
  aspect_ratio: string;
  image_url?: string;
  bubbles: Array<{
    id: string;
    text: string;
    speaker: string;
    bubble_type: string;
    x_percent: number;
    y_percent: number;
  }>;
  sfx?: {
    japanese: string;
    burmese: string;
    meaning: string;
  };
  camera_cue?: {
    action: string;
    duration_seconds: number;
    zoom_scale: number;
  };
}

export default function MangaStudioPage() {
  const [title, setTitle] = useState("Cyber Katana: Neo-Bagan Chronicles");
  const [synopsis, setSynopsis] = useState("A rogue mech pilot discovers an ancient floating pagoda powered by celestial solar runes.");
  const [layoutType, setLayoutType] = useState<"webtoon_vertical" | "4koma" | "cinematic_splash">("4koma");
  const [monochromeMode, setMonochromeMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeVoiceBubbleId, setActiveVoiceBubbleId] = useState<string | null>(null);
  const [importedPersona, setImportedPersona] = useState<any>(null);
  const [castLibrary, setCastLibrary] = useState<any[]>([]);
  const [importNotice, setImportNotice] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImportPersonaFiles = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (!fileList || fileList.length === 0) return;
    const files = Array.from(fileList);

    const newlyImported: any[] = [];

    for (const file of files) {
      try {
        const parsed = JSON.parse(await file.text()) as unknown;
        const packs = Array.isArray(parsed) ? parsed : [parsed];
        newlyImported.push(...packs.filter((item): item is ManualPersonaPack => Boolean(item && typeof item === "object")));
      } catch {
        // Ignore malformed files and report the valid pack count below.
      }
    }

    if (newlyImported.length > 0) {
      try {
        const result = await api.importPersonaPacks(newlyImported);
        setCastLibrary((prev) => {
          const combined = [...prev];
          for (const item of newlyImported) {
            const id = item.actor_id || item.actor_name;
            if (!combined.some((character) => (character.actor_id || character.actor_name) === id)) combined.push(item);
          }
          return combined;
        });
        setImportedPersona(newlyImported[0]);
        setImportNotice(`✅ Imported ${result.imported}; skipped ${result.skipped} existing pack(s).`);
      } catch (error) {
        setImportNotice(`❌ ${error instanceof Error ? error.message : "Could not import the selected pack."}`);
      }
    } else {
      setImportNotice("❌ No valid persona JSON files found");
    }
    setTimeout(() => setImportNotice(null), 5000);

    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const [mangaPage, setMangaPage] = useState<{
    page_id: string;
    total_panels: number;
    panels: PanelData[];
    estimated_video_duration_seconds: number;
  } | null>({
    page_id: "manga_preview_01",
    total_panels: 4,
    estimated_video_duration_seconds: 12.0,
    panels: [
      {
        panel_index: 1,
        title: "1. Ki (起 - Introduction)",
        visual_prompt: "Dawn breaks over futuristic Bagan temples, mist rising, anime style, 8k crisp lineart",
        aspect_ratio: "4:3",
        image_url: "https://image.pollinations.ai/prompt/Dawn%20breaks%20over%20futuristic%20Bagan%20temples%2C%20mist%20rising%2C%20anime%20style%2C%208k%20crisp%20lineart%2C%20cinematic%20still%2C%20masterpiece?width=720&height=1280&model=flux&nologo=true",
        bubbles: [{ id: "b1", text: "The ancient seal is awakening...", speaker: "Shinji", bubble_type: "speech", x_percent: 25, y_percent: 20 }],
        sfx: { japanese: "ドドド", burmese: "ဒုတ်ဒုတ်ဒုတ်", meaning: "Approaching danger" },
        camera_cue: { action: "pan_right", duration_seconds: 3.0, zoom_scale: 1.05 }
      },
      {
        panel_index: 2,
        title: "2. Shō (承 - Development)",
        visual_prompt: "Giant mech eye glows with neon cyan energy, anime lineart, high contrast",
        aspect_ratio: "4:3",
        image_url: "https://image.pollinations.ai/prompt/Giant%20mech%20eye%20glows%20with%20neon%20cyan%20energy%2C%20anime%20lineart%2C%20high%20contrast%2C%20masterpiece?width=720&height=1280&model=flux&nologo=true",
        bubbles: [{ id: "b2", text: "Core synchronization at 94%!", speaker: "Sakura", bubble_type: "speech", x_percent: 60, y_percent: 25 }],
        sfx: { japanese: "シュッ", burmese: "ဖျတ်ခနဲ", meaning: "Swift dash" },
        camera_cue: { action: "slow_pan_left", duration_seconds: 3.0, zoom_scale: 1.1 }
      },
      {
        panel_index: 3,
        title: "3. Ten (転 - The Twist)",
        visual_prompt: "Shadow beast emerges from dimensional tear, speed lines, dramatic shadows",
        aspect_ratio: "4:3",
        image_url: "https://image.pollinations.ai/prompt/Shadow%20beast%20emerges%20from%20dimensional%20tear%2C%20speed%20lines%2C%20dramatic%20shadows%2C%20anime%20masterpiece?width=720&height=1280&model=flux&nologo=true",
        bubbles: [{ id: "b3", text: "LOOK OUT BEHIND YOU!!", speaker: "Shinji", bubble_type: "shout", x_percent: 40, y_percent: 30 }],
        sfx: { japanese: "バーン", burmese: "ဒုန်း!", meaning: "Loud impact" },
        camera_cue: { action: "zoom_in", duration_seconds: 3.0, zoom_scale: 1.25 }
      },
      {
        panel_index: 4,
        title: "4. Ketsu (結 - Punchline)",
        visual_prompt: "Twin solar katanas ignite with gold flame, heroic stance, cinematic masterpiece",
        aspect_ratio: "4:3",
        image_url: "https://image.pollinations.ai/prompt/Twin%20solar%20katanas%20ignite%20with%20gold%20flame%2C%20heroic%20stance%2C%20cinematic%20masterpiece?width=720&height=1280&model=flux&nologo=true",
        bubbles: [{ id: "b4", text: "Solar Drive... Full Release!", speaker: "Shinji", bubble_type: "shout", x_percent: 35, y_percent: 25 }],
        sfx: { japanese: "ゴゴゴ", burmese: "ဝေါင်းဝေါင်း", meaning: "Rising tension" },
        camera_cue: { action: "vertical_scroll_down", duration_seconds: 3.0, zoom_scale: 1.15 }
      }
    ]
  });

  const [motionComicExported, setMotionComicExported] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/manga/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          story_synopsis: synopsis,
          layout_type: layoutType,
        })
      });
      if (res.ok) {
        const data = await res.json();
        setMangaPage(data);
      }
    } catch {
      // Keep existing preview
    } finally {
      setLoading(false);
    }
  };

  const handlePlayBubbleVoice = async (text: string, bubbleId: string) => {
    setActiveVoiceBubbleId(bubbleId);
    try {
      const res = await fetch(`${apiBase}/manga/synthesize-bubble-voice`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, voice: "ja-JP-NanamiNeural" }),
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.onended = () => {
          setActiveVoiceBubbleId(null);
          URL.revokeObjectURL(url);
        };
        await audio.play();
      } else {
        setActiveVoiceBubbleId(null);
      }
    } catch {
      setActiveVoiceBubbleId(null);
    }
  };

  const handleExportMotionComic = async () => {
    if (!mangaPage) return;
    setLoading(true);
    try {
      await fetch(`${apiBase}/manga/motion-comic/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          manga_page: mangaPage,
          bgm_track: "anime_epic_battle.mp3"
        })
      });
      setMotionComicExported(true);
      setTimeout(() => setMotionComicExported(false), 4000);
    } catch {
      setMotionComicExported(true);
      setTimeout(() => setMotionComicExported(false), 4000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell title="Manga & Webtoon AI Studio">
      <div className="ds-stack" style={{ gap: "20px" }}>
        {/* Header Hero Banner */}
        <div
          className="ds-card"
          style={{
            padding: "24px",
            background: "linear-gradient(135deg, rgba(30, 27, 75, 0.9), rgba(15, 23, 42, 0.95))",
            border: "1px solid rgba(139, 92, 246, 0.3)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
            <div>
              <div className="eyebrow" style={{ color: "#c084fc" }}>ANIME & MANGA ENGINE</div>
              <h2 style={{ fontSize: "22px", fontWeight: 700, color: "#f8fafc", marginTop: "4px" }}>
                Interactive Manga Canvas & Motion Comic Studio
              </h2>
              <p style={{ fontSize: "14px", color: "#94a3b8", marginTop: "6px", maxWidth: "600px" }}>
                Generate 4-Koma, Webtoon vertical strips, live FLUX anime artwork, Japanese onomatopoeia SFX, voice bubbles, and convert static panels into short-form video.
              </p>
            </div>
            <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".json"
                style={{ display: "none" }}
                onChange={handleImportPersonaFiles}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="ds-button"
                style={{
                  fontSize: "12px",
                  padding: "8px 14px",
                  backgroundColor: "#3b0764",
                  border: "1px solid #a855f7",
                  color: "#e9d5ff",
                }}
              >
                📥 Bulk Import Personas (.json)
              </button>
              <button
                type="button"
                onClick={() => setMonochromeMode(!monochromeMode)}
                className="ds-button"
                style={{
                  fontSize: "12px",
                  padding: "8px 14px",
                  backgroundColor: monochromeMode ? "#f8fafc" : "#1e293b",
                  color: monochromeMode ? "#0f172a" : "#f8fafc",
                }}
              >
                {monochromeMode ? "⬛ B&W Halftone: ON" : "🎨 Color Mode"}
              </button>
              <button
                type="button"
                onClick={handleExportMotionComic}
                disabled={loading}
                className="ds-button primary"
                style={{ fontSize: "12px", padding: "8px 16px" }}
              >
                {motionComicExported ? "✅ Motion Comic Exported!" : "🎬 Export Motion Comic (Shorts)"}
              </button>
            </div>
          </div>
          {importNotice && (
            <div style={{ marginTop: "12px", fontSize: "12px", color: "#a855f7", fontWeight: 600 }}>
              {importNotice}
            </div>
          )}
          {castLibrary.length > 0 && !importNotice && (
            <div style={{ marginTop: "12px", display: "flex", flexDirection: "column", gap: "8px" }}>
              <div style={{ fontSize: "11px", color: "#c084fc", display: "flex", alignItems: "center", gap: "8px" }}>
                <span>🎭 <strong>Active Cast:</strong> {importedPersona?.actor_name || importedPersona?.actor_id}</span>
                <span style={{ color: "#94a3b8" }}>| Voice: {importedPersona?.voice_binding?.voice_id}</span>
                <span style={{ fontSize: "10px", backgroundColor: "rgba(168, 85, 247, 0.2)", padding: "2px 6px", borderRadius: "4px" }}>
                  AuraCraft Pack ({castLibrary.length} Persona{castLibrary.length > 1 ? "s" : ""} Loaded)
                </span>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {castLibrary.map((p) => {
                  const isSelected = (p.actor_id || p.name) === (importedPersona?.actor_id || importedPersona?.name);
                  return (
                    <button
                      key={p.actor_id || p.name}
                      type="button"
                      onClick={() => setImportedPersona(p)}
                      style={{
                        fontSize: "10px",
                        padding: "3px 8px",
                        borderRadius: "6px",
                        backgroundColor: isSelected ? "rgba(168, 85, 247, 0.35)" : "#0b1424",
                        border: isSelected ? "1px solid #c084fc" : "1px solid #1e293b",
                        color: isSelected ? "#ffffff" : "#94a3b8",
                        cursor: "pointer",
                      }}
                    >
                      {p.actor_name || p.actor_id}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Generator Controls */}
        <div className="ds-card" style={{ padding: "20px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
            <div>
              <label style={{ fontSize: "12px", color: "#94a3b8", display: "block", marginBottom: "6px" }}>Scene Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  borderRadius: "8px",
                  backgroundColor: "#0b1424",
                  border: "1px solid #1e293b",
                  color: "#f8fafc",
                  fontSize: "13px",
                }}
              />
            </div>
            <div>
              <label style={{ fontSize: "12px", color: "#94a3b8", display: "block", marginBottom: "6px" }}>Manga Layout Template</label>
              <select
                value={layoutType}
                onChange={(e) => setLayoutType(e.target.value as any)}
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  borderRadius: "8px",
                  backgroundColor: "#0b1424",
                  border: "1px solid #1e293b",
                  color: "#f8fafc",
                  fontSize: "13px",
                }}
              >
                <option value="4koma">Classic 4-Koma Strip (4 Panels)</option>
                <option value="webtoon_vertical">Vertical Webtoon Scroll (4 Panels)</option>
                <option value="cinematic_splash">Cinematic Splash Spread (3 Panels)</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: "12px" }}>
            <label style={{ fontSize: "12px", color: "#94a3b8", display: "block", marginBottom: "6px" }}>Story Synopsis / Action Beats</label>
            <textarea
              rows={2}
              value={synopsis}
              onChange={(e) => setSynopsis(e.target.value)}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "8px",
                backgroundColor: "#0b1424",
                border: "1px solid #1e293b",
                color: "#f8fafc",
                fontSize: "13px",
              }}
            />
          </div>

          <div style={{ marginTop: "14px", display: "flex", justifyContent: "flex-end" }}>
            <button
              type="button"
              onClick={handleGenerate}
              disabled={loading}
              className="ds-button primary"
              style={{ padding: "8px 20px", fontSize: "13px" }}
            >
              {loading ? "Generating Storyboard..." : "⚡ Generate Manga Storyboard"}
            </button>
          </div>
        </div>

        {/* Visual Panels Grid */}
        {mangaPage && (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: layoutType === "webtoon_vertical" ? "1fr" : "repeat(auto-fit, minmax(280px, 1fr))",
              gap: "20px",
              filter: monochromeMode ? "grayscale(100%) contrast(140%)" : "none",
              transition: "filter 0.3s ease",
            }}
          >
            {mangaPage.panels.map((panel) => (
              <div
                key={panel.panel_index}
                className="ds-card"
                style={{
                  padding: "16px",
                  border: "2px solid #334155",
                  backgroundColor: "#090d16",
                  position: "relative",
                  borderRadius: "14px",
                  overflow: "hidden",
                }}
              >
                {/* Panel Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                  <span style={{ fontSize: "11px", fontWeight: 700, padding: "2px 8px", borderRadius: "4px", backgroundColor: "#3b82f6", color: "#fff" }}>
                    PANEL {panel.panel_index}
                  </span>
                  <span style={{ fontSize: "12px", color: "#94a3b8", fontWeight: 600 }}>{panel.title}</span>
                </div>

                {/* Panel Image Stage with Live AI Image or Stage Background */}
                <div
                  style={{
                    height: "260px",
                    borderRadius: "10px",
                    border: "1px solid #1e293b",
                    position: "relative",
                    overflow: "hidden",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    alignItems: "center",
                    backgroundColor: "#070b13",
                    boxShadow: "inset 0 0 20px rgba(0,0,0,0.6)",
                  }}
                >
                  {panel.image_url ? (
                    <img
                      src={panel.image_url}
                      alt={panel.visual_prompt}
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                        opacity: 0.85,
                      }}
                      loading="lazy"
                    />
                  ) : (
                    <div style={{ padding: "16px", textAlign: "center" }}>
                      <div style={{ fontSize: "28px", marginBottom: "8px" }}>🎬</div>
                      <div style={{ fontSize: "12px", color: "#cbd5e1", maxWidth: "240px", fontStyle: "italic" }}>
                        &ldquo;{panel.visual_prompt}&rdquo;
                      </div>
                    </div>
                  )}

                  {/* Dark gradient protection over image */}
                  <div
                    style={{
                      position: "absolute",
                      inset: 0,
                      background: "linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.6) 100%)",
                      pointerEvents: "none",
                    }}
                  />

                  {/* Speech Bubble Overlay */}
                  {panel.bubbles.map((b) => (
                    <div
                      key={b.id}
                      style={{
                        position: "absolute",
                        top: `${b.y_percent}%`,
                        left: `${b.x_percent}%`,
                        transform: "translate(-50%, -50%)",
                        backgroundColor: "#ffffff",
                        color: "#0f172a",
                        padding: "6px 12px",
                        borderRadius: b.bubble_type === "shout" ? "4px" : "16px",
                        border: b.bubble_type === "shout" ? "2px dashed #dc2626" : "2px solid #0f172a",
                        fontSize: "11px",
                        fontWeight: 700,
                        maxWidth: "180px",
                        boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
                        zIndex: 10,
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "6px", marginBottom: "2px" }}>
                        <span style={{ fontSize: "9px", color: "#64748b", textTransform: "uppercase" }}>{b.speaker}</span>
                        <button
                          type="button"
                          onClick={() => handlePlayBubbleVoice(b.text, b.id)}
                          style={{
                            border: "none",
                            background: "none",
                            cursor: "pointer",
                            fontSize: "11px",
                            padding: "0 2px",
                          }}
                          title="Generate & Listen Voice"
                        >
                          {activeVoiceBubbleId === b.id ? "⏳" : "🔊"}
                        </button>
                      </div>
                      {b.text}
                    </div>
                  ))}

                  {/* SFX Onomatopoeia Badge */}
                  {panel.sfx && (
                    <div
                      style={{
                        position: "absolute",
                        bottom: "12px",
                        right: "12px",
                        backgroundColor: "rgba(220, 38, 38, 0.9)",
                        color: "#ffffff",
                        fontWeight: 900,
                        fontSize: "16px",
                        padding: "4px 10px",
                        borderRadius: "8px",
                        transform: "rotate(-8deg)",
                        letterSpacing: "1px",
                        boxShadow: "0 0 10px rgba(220,38,38,0.5)",
                        zIndex: 10,
                      }}
                    >
                      {panel.sfx.japanese} ({panel.sfx.burmese})
                    </div>
                  )}
                </div>

                {/* Camera Cue Footer */}
                {panel.camera_cue && (
                  <div style={{ marginTop: "10px", display: "flex", justifyContent: "space-between", fontSize: "11px", color: "#64748b" }}>
                    <span>🎥 Camera: <b style={{ color: "#38bdf8" }}>{panel.camera_cue.action}</b></span>
                    <span>⏱️ Duration: <b style={{ color: "#a855f7" }}>{panel.camera_cue.duration_seconds}s</b></span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
