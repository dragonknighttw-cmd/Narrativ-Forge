"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../../components/app-shell";
import { ErrorState } from "../../../../components/domain-forms";
import { api, Script } from "../../../../lib/api";

const HOOK_PRESETS = [
  { type: "question", label: "Question (မေးခွန်း)", template: "သင်ရော [အကြောင်းအရာ] အကြောင်းကို တကယ်သိပါသလား?" },
  { type: "shock", label: "Shock (အံ့အားသင့်ဖွယ်)", template: "လူ ၉၀% လုံးဝမသိကြသေးတဲ့ [အကြောင်းအရာ] ရဲ့ လျှို့ဝှက်ချက်!" },
  { type: "mystery", label: "Mystery (ဆန်းကြယ်မှု)", template: "ဒီအရာကို မမြင်ဖူးသေးရင် သင့်ဘဝမှာ ကြီးမားတဲ့ အရာတစ်ခု လွတ်သွားပါပြီ။" },
  { type: "warning", label: "Warning (သတိပေးချက်)", template: "ဒီအမှားကို လုံးဝမလုပ်ပါနဲ့! မဟုတ်ရင် [ဆိုးကျိုး] ဖြစ်လာနိုင်ပါတယ်။" },
  { type: "personal_story", label: "Personal Story (ကိုယ်တွေ့)", template: "ကျွန်တော် စတင်တုန်းက ဒီနည်းလမ်းကို ဘယ်သူမှ မပြောပြခဲ့ပါဘူး…" },
  { type: "contrarian", label: "Contrarian (ဆန့်ကျင်ဘက်)", template: "လူတိုင်းထင်နေတာ မှားနေပါတယ်။ အမှန်ကတော့…" },
  { type: "cliffhanger", label: "Cliffhanger (ဇာတ်ရှိန်)", template: "နောက်ဆုံးမှာ ဘာဖြစ်သွားလဲဆိုတာ သိရင် သင် အံ့ဩသွားပါလိမ့်မယ်။" },
  { type: "number", label: "Number (ကိန်းဂဏန်း)", template: "သင့်ဘဝကို ပြောင်းလဲပေးနိုင်တဲ့ အရေးကြီးအချက် ၃ ချက်!" },
];

export default function ScriptStudioPage() {
  const { id } = useParams<{ id: string }>();
  const [scripts, setScripts] = useState<Script[]>([]);
  const [active, setActive] = useState<Script | null>(null);
  const [content, setContent] = useState("");
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [saveState, setSaveState] = useState<"saved" | "dirty" | "saving" | "conflict">("saved");
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // AI Script Assistant State
  const [aiIdea, setAiIdea] = useState("");
  const [aiCategory, setAiCategory] = useState("entertainment");
  const [selectedHook, setSelectedHook] = useState(HOOK_PRESETS[0].type);
  const [aiBusy, setAiBusy] = useState(false);
  const [aiMessage, setAiMessage] = useState("");

  async function load() {
    try {
      setError("");
      const result = await api.listScripts(id);
      setScripts(result);
      if (active) {
        const current = result.find(item => item.id === active.id);
        if (current) {
          setActive(current);
          setSaveState("saved");
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load scripts");
    }
  }

  useEffect(() => {
    if (id) load();
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, [id]);

  async function createNew(version: boolean) {
    if (!content.trim() && version) return;
    setBusy(true);
    setError("");
    try {
      const created = version
        ? await api.createScriptVersion(id, { title: title || undefined, content })
        : await api.createScript(id, { title: title || undefined, content });
      setScripts(current => [created, ...current.filter(item => item.id !== created.id)]);
      setActive(created);
      setTitle(created.title || "");
      setContent(created.content);
      setSaveState("saved");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save script");
    } finally {
      setBusy(false);
    }
  }

  function selectScript(script: Script) {
    setActive(script);
    setTitle(script.title || "");
    setContent(script.content);
    setSaveState("saved");
    setError("");
  }

  async function autosave() {
    if (!active?.is_current || saveState === "saving") return;
    setSaveState("saving");
    try {
      const updated = await api.updateScript(id, active.id, {
        title: title || undefined,
        content,
        expected_row_version: active.row_version,
      });
      setActive(updated);
      setScripts(current => current.map(item => item.id === updated.id ? updated : item));
      setSaveState("saved");
      setError("");
    } catch (e) {
      setSaveState("conflict");
      setError(e instanceof Error ? e.message : "Autosave failed");
    }
  }

  useEffect(() => {
    if (!active?.is_current) return;
    setSaveState("dirty");
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => void autosave(), 900);
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, [content, title, active?.id]);

  async function handleAiPlan() {
    if (!aiIdea.trim()) return;
    setAiBusy(true);
    setAiMessage("");
    setError("");
    try {
      const hookPreset = HOOK_PRESETS.find(h => h.type === selectedHook);
      const combinedIdea = `${hookPreset ? `[Hook: ${hookPreset.label}] ` : ""}${aiIdea.trim()}`;
      const res = await api.autoPlanEpisode(id, { idea: combinedIdea, category: aiCategory });
      setContent(res.script.content);
      setTitle(`AI Draft - ${aiCategory}`);
      setAiMessage(`Generated script v${res.script.version} and ${res.scenes.length} structured scenes successfully!`);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "AI generation failed");
    } finally {
      setAiBusy(false);
    }
  }

  return <AppShell title="Script Studio">
    <section className="card" style={{ marginBottom: "1.5rem", borderLeft: "4px solid #6366f1" }}>
      <div className="eyebrow" style={{ color: "#6366f1" }}>AI SCRIPT & SCENE ASSISTANT</div>
      <h2>Generate Full Burmese Script & Scenes with AI</h2>
      <p className="muted">Select a canonical hook family, enter your concept, and the AI will draft the script and scene breakdown automatically.</p>
      {aiMessage && <div style={{ padding: "0.75rem 1rem", backgroundColor: "rgba(99,102,241,0.1)", borderRadius: "6px", color: "#6366f1", marginBottom: "1rem" }}>{aiMessage}</div>}
      <div className="stack-form">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1rem" }}>
          <div>
            <label style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", fontWeight: 500 }}>Hook Family (၈ မျိုး)</label>
            <select
              value={selectedHook}
              onChange={e => setSelectedHook(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #334155", background: "#0f172a", color: "#f8fafc" }}
            >
              {HOOK_PRESETS.map(h => (
                <option key={h.type} value={h.type}>{h.label}</option>
              ))}
            </select>
            <p className="muted burmese-text" style={{ fontSize: "0.8rem", marginTop: "0.25rem" }}>
              Template: {HOOK_PRESETS.find(h => h.type === selectedHook)?.template}
            </p>
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", fontWeight: 500 }}>Category</label>
            <select
              value={aiCategory}
              onChange={e => setAiCategory(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #334155", background: "#0f172a", color: "#f8fafc" }}
            >
              <option value="entertainment">Entertainment (ဖျော်ဖြေရေး)</option>
              <option value="education">Education (ဗဟုသုတ)</option>
              <option value="mystery">Mystery (ဆန်းကြယ်မှု)</option>
              <option value="technology">Technology (နည်းပညာ)</option>
              <option value="lifestyle">Lifestyle (လူနေမှုစတိုင်)</option>
            </select>
          </div>
        </div>
        <div>
          <label style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", fontWeight: 500 }}>Core Idea / Concept (မြန်မာဘာသာဖြင့် အကြောင်းအရာ)</label>
          <input
            value={aiIdea}
            onChange={e => setAiIdea(e.target.value)}
            placeholder="ဥပမာ - ရှေးမြန်မာဘုရင်တွေ အသုံးပြုခဲ့တဲ့ လျှို့ဝှက်ကုဒ်စနစ်"
          />
        </div>
        <div>
          <button
            className="primary"
            disabled={aiBusy || !aiIdea.trim()}
            onClick={handleAiPlan}
          >
            {aiBusy ? "Generating Script & Scenes…" : "AI Generate Script & Scenes"}
          </button>
        </div>
      </div>
    </section>

    <section className="card">
      <div className="eyebrow">SCRIPT WORKFLOW</div>
      <h2>Draft and version the episode script</h2>
      <p className="muted">Current scripts autosave with optimistic locking. Historical versions remain immutable.</p>
      {error && <ErrorState message={error} retry={load} />}
      <div className="stack-form">
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Script title" />
        <textarea className="burmese-text" value={content} onChange={e => setContent(e.target.value)} placeholder="Write the Burmese script…" rows={14} />
        <div className="inline-form">
          <button className="primary" disabled={busy || !!active} onClick={() => createNew(false)}>Create script</button><button disabled={busy} onClick={() => { setActive(null); setTitle(""); setContent(""); setSaveState("saved"); setError(""); }}>New draft</button>
          <button disabled={busy || !content.trim()} onClick={() => createNew(true)}>Save new version</button>
          {active?.is_current && <span className="muted">{saveState === "saving" ? "Saving…" : saveState === "dirty" ? "Unsaved changes…" : saveState === "conflict" ? "Conflict — reload before continuing" : "Saved"}</span>}
        </div>
      </div>
    </section>
    <section className="card">
      <div className="eyebrow">VERSIONS</div>
      {scripts.length === 0 ? <div className="empty-state">No script versions yet.</div> : <div className="list">
        {scripts.map(s => <article className="list-card" key={s.id}>
          <div><strong>v{s.version} {s.title || "Untitled"}</strong><p className="muted">{s.status} · {s.is_current ? "current" : "archived version"}</p></div>
          <button className="text-button" onClick={() => selectScript(s)}>Load</button>
        </article>)}
      </div>}
    </section>
  </AppShell>;
}
