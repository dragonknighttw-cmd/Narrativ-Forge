"use client";

import { FormEvent, useState } from "react";

export function InlineForm({ label, placeholder, button, onSubmit }: { label: string; placeholder: string; button: string; onSubmit: (value: string) => Promise<void> }) {
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!value.trim()) return;
    setBusy(true);
    try { await onSubmit(value.trim()); setValue(""); } finally { setBusy(false); }
  }
  return <form className="inline-form" onSubmit={submit}><input aria-label={label} placeholder={placeholder} value={value} onChange={e => setValue(e.target.value)} /><button className="primary" disabled={busy}>{busy ? "Saving…" : button}</button></form>;
}

export function ErrorState({ message, retry }: { message: string; retry?: () => void }) {
  return <div className="error" role="alert">{message}{retry && <button className="text-button" onClick={retry}>Retry</button>}</div>;
}
