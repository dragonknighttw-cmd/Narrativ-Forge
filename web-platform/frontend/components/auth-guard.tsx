"use client";

import { ReactNode, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../lib/api";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<"checking" | "authenticated" | "error">("checking");

  useEffect(() => {
    api.me()
      .then(() => setState("authenticated"))
      .catch(() => {
        setState("error");
        router.replace("/login");
      });
  }, [router]);

  if (state === "checking") {
    return <main className="center-state"><div className="card"><div className="eyebrow">SESSION</div><h2>Checking access…</h2><p className="muted">Your workspace session is being verified.</p></div></main>;
  }

  if (state === "error") return null;
  return <>{children}</>;
}
