"use client";
import { useEffect, useState } from "react";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";

const TYPES=["question","shock","mystery","warning","personal_story","contrarian","cliffhanger"];

export default function HookLibraryPage(){
  const [items,setItems]=useState<any[]>([]);
  const [text,setText]=useState("");
  const [type,setType]=useState("question");
  const [topic,setTopic]=useState("");
  const [error,setError]=useState("");
  async function load(){try{const r=await fetch("/api/v1/hooks",{credentials:"include"});const b=await r.json();if(!r.ok)throw new Error(b.detail??"Failed to load hooks");setItems(b)}catch(e){setError(e instanceof Error?e.message:"Failed to load hooks")}}
  useEffect(()=>{load()},[]);
  async function add(){try{const r=await fetch("/api/v1/hooks",{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify({hook_text:text,hook_type:type,topic:topic||null})});const b=await r.json();if(!r.ok)throw new Error(b.detail??"Failed to add hook");setText("");setTopic("");await load()}catch(e){setError(e instanceof Error?e.message:"Failed to add hook")}}
  return <AppShell title="Hook Library"><section className="card"><div className="eyebrow">HOOK LIBRARY</div><p className="muted">Reusable hooks and observed performance data. Default changes remain human-controlled.</p>{error&&<ErrorState message={error} retry={load}/>}<div className="inline-form"><input value={text} onChange={e=>setText(e.target.value)} placeholder="Hook text"/><select value={type} onChange={e=>setType(e.target.value)}>{TYPES.map(x=><option key={x}>{x}</option>)}</select><input value={topic} onChange={e=>setTopic(e.target.value)} placeholder="Topic"/><button className="primary" disabled={!text.trim()} onClick={add}>Add hook</button></div></section><section className="card"><div className="list">{items.map(x=><div className="list-card" key={x.id}><div><strong>{x.hook_text}</strong><p className="muted">{x.hook_type} · used {x.used_count} · score {x.performance_score??"—"}</p></div><span className="muted">{x.is_default?"DEFAULT":""}</span></div>)}</div>{!items.length&&<div className="empty-state">No hooks yet.</div>}</section></AppShell>
}