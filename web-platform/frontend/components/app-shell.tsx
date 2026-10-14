"use client";

import Link from "next/link";
import { ReactNode, useState } from "react";
import { AuthGuard } from "./auth-guard";

const sections = [
  ["Workspace", [["Dashboard","/dashboard"],["Ideas","/ideas"],["Series","/series"],["Episodes","/episodes"]]],
  ["Production", [["Script Studio","/script-studio"],["Scene Breakdown","/scene-breakdown"],["Asset Library","/assets"],["Processing Queue","/processing"],["Subtitle Studio","/subtitles"]]],
  ["Control", [["Review Center","/review"],["AI Usage & Limits","/usage"],["Drive Export","/export"],["Publishing Preparation","/publishing-prep"],["Manual Production Log","/manual-log"],["Hook Library","/hooks"],["App Analytics","/analytics"],["Subtitle Presets","/subtitle-presets"]]],
  ["System", [["Settings","/settings"]]],
] as const;

export function AppShell({ title, children }: { title: string; children: ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return <AuthGuard>
    <div className="shell">
      <aside className="sidebar">
        <Link href="/dashboard" className="logo"><span>NF</span><strong>Narrativ Forge</strong></Link>
        {sections.map(([section, items]) => <div className="nav-group" key={section}>
          <div className="nav-label">{section}</div>
          {items.map(([label, href]) => <Link className="nav-link" href={href} key={href}>{label}</Link>)}
        </div>)}
      </aside>
      <main className="main">
        <header className="topbar">
          <div className="ds-row">
            <button
              className="mobile-nav-toggle"
              type="button"
              aria-label={mobileMenuOpen ? "Close navigation" : "Open navigation"}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? "✕" : "☰"}
            </button>
            <div>
              <div className="eyebrow">STUDIO WORKSPACE</div>
              <h1>{title}</h1>
            </div>
          </div>
          <div className="ds-row">
            <div className="ds-badge" style={{ backgroundColor: "rgba(16, 185, 129, 0.08)", borderColor: "rgba(16, 185, 129, 0.25)", color: "#10b981", fontSize: "11px", display: "flex", gap: "6px" }}>
              <span style={{ display: "inline-block", width: "6px", height: "6px", borderRadius: "50%", backgroundColor: "#10b981" }}></span>
              Telegram Topic #Narrativ-Forge
            </div>
            <Link className="avatar" href="/settings">NF</Link>
          </div>
        </header>
        {mobileMenuOpen && (
          <nav className="mobile-drawer" aria-label="Mobile navigation">
            <div className="ds-stack">
              {sections.map(([section, items]) => (
                <div className="nav-group" key={section}>
                  <div className="nav-label">{section}</div>
                  {items.map(([label, href]) => (
                    <Link
                      className="nav-link"
                      href={href}
                      key={href}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {label}
                    </Link>
                  ))}
                </div>
              ))}
            </div>
          </nav>
        )}
        <div className="content">{children}</div>
      </main>
    </div>
  </AuthGuard>;
}
