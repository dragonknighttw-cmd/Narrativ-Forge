import Link from "next/link";
import { ReactNode } from "react";

const sections = [
  ["Workspace", [["Dashboard","/dashboard"],["Ideas","/ideas"],["Series","/series"],["Episodes","/episodes"]]],
  ["Production", [["Script Studio","/script-studio"],["Scene Breakdown","/scene-breakdown"],["Asset Library","/assets"],["Processing Queue","/processing"],["Subtitle Studio","/subtitles"]]],
  ["Control", [["Review Center","/review"],["Drive Export","/export"],["Manual Production Log","/manual-log"],["Hook Library","/hooks"],["Subtitle Presets","/subtitle-presets"]]],
  ["System", [["Settings","/settings"]]],
] as const;

export function AppShell({ title, children }: { title: string; children: ReactNode }) {
  return <div className="shell">
    <aside className="sidebar">
      <Link href="/dashboard" className="logo"><span>NF</span><strong>Narrativ Forge</strong></Link>
      {sections.map(([section, items]) => <div className="nav-group" key={section}>
        <div className="nav-label">{section}</div>
        {items.map(([label, href]) => <Link className="nav-link" href={href} key={href}>{label}</Link>)}
      </div>)}
    </aside>
    <main className="main">
      <header className="topbar"><div><div className="eyebrow">PRIVATE WORKSPACE</div><h1>{title}</h1></div><Link className="avatar" href="/settings">NF</Link></header>
      <div className="content">{children}</div>
    </main>
  </div>;
}