"use client";
import { useEffect,useState } from "react";
import { AppShell } from "../../components/app-shell";
import { ErrorState } from "../../components/domain-forms";

export default function AnalyticsPage(){
 const [data,setData]=useState<any>(null); const [error,setError]=useState("");
 async function load(){try{const r=await fetch("/api/v1/analytics",{credentials:"include"});const b=await r.json();if(!r.ok)throw new Error(b.detail??"Failed to load analytics");setData(b)}catch(e){setError(e instanceof Error?e.message:"Failed to load analytics")}}
 useEffect(()=>{load()},[]);
 return <AppShell title="App Analytics"><section className="card"><div className="eyebrow">PRODUCTION + SOCIAL ANALYTICS</div>{error&&<ErrorState message={error} retry={load}/>}<div className="kpi-grid">{data&&Object.entries(data).map(([k,v])=><div className="kpi-card" key={k}><div className="muted">{k.replaceAll("_"," ")}</div><strong>{String(v)}</strong></div>)}</div>{!data&&!error&&<div className="empty-state">Loading analytics…</div>}</section></AppShell>
}