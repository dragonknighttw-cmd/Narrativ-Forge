"use client";

import Link from "next/link";
import { ReactNode, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import {
  Activity, BarChart3, BookOpen, Captions, Clapperboard, ClipboardCheck,
  Film, FolderOpen, Gauge, HardDriveDownload, Image, LayoutDashboard,
  Lightbulb, ListChecks, Menu, ScrollText, Send, Settings2, SlidersHorizontal,
  Sparkles, Workflow, X, type LucideIcon,
} from "lucide-react";
import { AuthGuard } from "./auth-guard";
import { NarrativLogo } from "./NarrativLogo";

const sections: { label: string; items: { label: string; href: string; icon: LucideIcon }[] }[] = [
  { label: "Workspace", items: [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Ideas", href: "/ideas", icon: Lightbulb },
    { label: "Series", href: "/series", icon: BookOpen },
    { label: "Episodes", href: "/episodes", icon: Film },
  ]},
  { label: "Production", items: [
    { label: "Script Studio", href: "/script-studio", icon: Clapperboard },
    { label: "Manga & Webtoon AI", href: "/manga-studio", icon: BookOpen },
    { label: "Video Clip Composer", href: "/video-composer", icon: Film },
    { label: "Movie Recap AI", href: "/recap", icon: Clapperboard },
    { label: "Workflow Canvas", href: "/workflows", icon: Workflow },
    { label: "Scene Breakdown", href: "/scene-breakdown", icon: ListChecks },
    { label: "Asset Library", href: "/assets", icon: FolderOpen },
    { label: "Processing Queue", href: "/processing", icon: Activity },
    { label: "Subtitle Studio", href: "/subtitles", icon: Captions },
  ]},
  { label: "Control", items: [
    { label: "Review Center", href: "/review", icon: ClipboardCheck },
    { label: "AI Usage & Limits", href: "/usage", icon: Gauge },
    { label: "Drive Export", href: "/export", icon: HardDriveDownload },
    { label: "Publishing Preparation", href: "/publishing-prep", icon: Send },
    { label: "Manual Production Log", href: "/manual-log", icon: ScrollText },
    { label: "Hook Library", href: "/hooks", icon: Sparkles },
    { label: "App Analytics", href: "/analytics", icon: BarChart3 },
    { label: "Subtitle Presets", href: "/subtitle-presets", icon: SlidersHorizontal },
  ]},
  { label: "System", items: [
    { label: "Settings", href: "/settings", icon: Settings2 },
  ]},
];

function Navigation({ onNavigate, pathname }: { onNavigate?: () => void; pathname: string }) {
  return (
    <nav className="app-navigation" aria-label="Primary navigation">
      {sections.map((section) => (
        <section className="nav-group" key={section.label} aria-labelledby={`nav-${section.label.toLowerCase()}`}>
          <h2 className="nav-label" id={`nav-${section.label.toLowerCase()}`}>{section.label}</h2>
          <div className="nav-items">
            {section.items.map(({ label, href, icon: Icon }) => {
              const episodeSubroute = pathname.match(/^\/episodes\/[^/]+\/(script|manga|composer|scenes|assets|subtitle|review|export)(?:\/|$)/)?.[1];
              const episodeRouteTarget: Record<string, string> = {
                script: "/script-studio", manga: "/manga-studio", composer: "/video-composer",
                scenes: "/scene-breakdown", assets: "/assets", subtitle: "/subtitles",
                review: "/review", export: "/export",
              };
              const active = pathname === href || pathname.startsWith(`${href}/`)
                || (episodeSubroute ? episodeRouteTarget[episodeSubroute] === href : false);
              return (
                <Link
                  className={`nav-link${active ? " is-active" : ""}`}
                  href={href}
                  key={href}
                  aria-current={active ? "page" : undefined}
                  onClick={onNavigate}
                >
                  <Icon size={17} strokeWidth={1.8} aria-hidden="true" />
                  <span>{label}</span>
                </Link>
              );
            })}
          </div>
        </section>
      ))}
    </nav>
  );
}

export function AppShell({ title, children }: { title: string; children: ReactNode }) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!mobileMenuOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMobileMenuOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [mobileMenuOpen]);

  return (
    <AuthGuard>
      <div className="shell">
        <aside className="sidebar" aria-label="Workspace sidebar">
          <Link href="/dashboard" className="logo" aria-label="Narrativ Forge dashboard">
            <NarrativLogo size={38} />
          </Link>
          <div className="sidebar-workspace">
            <span className="workspace-mark">NF</span>
            <span><strong>Production workspace</strong><small>Private studio</small></span>
          </div>
          <Navigation pathname={pathname} />
          <div className="sidebar-footer">
            <span className="sidebar-footer-dot" aria-hidden="true" />
            <span>Private workspace</span>
            <span className="sidebar-footer-version">NF</span>
          </div>
        </aside>

        <main className="main">
          <header className="topbar">
            <div className="topbar-heading">
              <button
                className="mobile-nav-toggle"
                type="button"
                aria-label={mobileMenuOpen ? "Close navigation" : "Open navigation"}
                aria-expanded={mobileMenuOpen}
                aria-controls="mobile-navigation"
                onClick={() => setMobileMenuOpen((open) => !open)}
              >
                {mobileMenuOpen ? <X size={19} /> : <Menu size={19} />}
              </button>
              <div>
                <div className="topbar-breadcrumb"><span>STUDIO</span><span aria-hidden="true">/</span><span>WORKSPACE</span></div>
                <h1>{title}</h1>
              </div>
            </div>
            <div className="topbar-actions">
              <div className="workspace-status" aria-label="Narrativ Forge Telegram topic 6">
                <span className="status-indicator" aria-hidden="true" />
                <span>Telegram · Topic 6</span>
              </div>
              <Link className="avatar" href="/settings" aria-label="Open workspace settings">NF</Link>
            </div>
          </header>

          {mobileMenuOpen && (
            <>
              <button
                className="mobile-nav-backdrop"
                type="button"
                aria-label="Close navigation menu"
                onClick={() => setMobileMenuOpen(false)}
              />
              <aside className="mobile-drawer" id="mobile-navigation" aria-label="Mobile workspace navigation">
                <Navigation pathname={pathname} onNavigate={() => setMobileMenuOpen(false)} />
              </aside>
            </>
          )}

          <div className="content">{children}</div>
        </main>
      </div>
    </AuthGuard>
  );
}
