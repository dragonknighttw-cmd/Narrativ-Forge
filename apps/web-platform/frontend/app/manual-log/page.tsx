"use client";
import { useEffect, useState } from "react";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";

export default function ManualProductionLogPage(){
 const [items,setItems]=useState<any[]>([]);
 const [topic,setTopic]=useState("");
 const [production,setProduction]=useState("");
 const [error,setError]=useState("");
 async function load(){try{const r=await fetch("/api/v1/manual-production-logs",{credentials:"include"});const b=await r.json();if(!r.ok)throw new Error(b.detail??"Failed to load logs");setItems(b)}catch(e){setError(e instanceof Error?e.message:"Failed to load logs")}}
 useEffect(()=>{load()},[]);
 async function add(){try{const r=await fetch("/api/v1/manual-production-logs",{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic,production_time_seconds:production?Number(production):null})});const b=await r.json();if(!r.ok)throw new Error(b.detail??"Failed to save log");setTopic("");setProduction("");await load()}catch(e){setError(e instanceof Error?e.message:"Failed to save log")}}
 return <AppShell title="Manual Production Log"><section className="card"><div className="eyebrow">MANUAL WORKFLOW DATA</div><p className="muted">Capture the manual workflow so it can become reusable production knowledge.</p>{error&&<ErrorState message={error} retry={load}/>}<div className="inline-form"><input value={topic} onChange={e=>setTopic(e.target.value)} placeholder="Topic" /><input type="number" min="0" value={production} onChange={e=>setProduction(e.target.value)} placeholder="Production time (seconds)" /><button className="primary" disabled={!topic.trim()} onClick={add}>Save log</button></div></section><section className="card"><div className="list">{items.map(x=><div className="list-card" key={x.id}><strong>{x.topic}</strong><span className="muted">{x.production_time_seconds??"—"} sec · {new Date(x.created_at).toLocaleString()}</span></div>)}</div>{!items.length&&<div className="empty-state">No production logs yet.</div>}</section></AppShell>
}