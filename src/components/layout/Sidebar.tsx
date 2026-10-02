import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { cn } from "../../lib/utils";
import { Logo } from "./Logo";
import {
  LayoutDashboard, Lightbulb, Film, Clapperboard, PenLine,
  LayoutGrid, FileVideo, FileText, ListChecks, Cpu,
  CheckSquare, History, HardDrive, Share2, BookOpen,
  BarChart3, Activity, Settings, ChevronLeft, MoreVertical,
  Zap, Database, FolderClosed,
} from "lucide-react";

interface NavGroup {
  label: string;
  items: { label: string; path: string; icon: React.ReactNode }[];
}

const navGroups: NavGroup[] = [
  {
    label: "Overview",
    items: [
      { label: "Studio Overview", path: "/dashboard", icon: <LayoutDashboard size={16} /> },
    ],
  },
  {
    label: "Content",
    items: [
      { label: "Content Ideas", path: "/ideas", icon: <Lightbulb size={16} /> },
      { label: "All Series", path: "/series", icon: <Film size={16} /> },
      { label: "Episodes", path: "/episodes", icon: <Clapperboard size={16} /> },
      { label: "Hook Library", path: "/hooks", icon: <Zap size={16} /> },
    ],
  },
  {
    label: "Production",
    items: [
      { label: "Script Studio", path: "/scripts", icon: <PenLine size={16} /> },
      { label: "Scene Breakdown", path: "/scenes", icon: <LayoutGrid size={16} /> },
      { label: "Asset Library", path: "/assets", icon: <FolderClosed size={16} /> },
      { label: "Video Projects", path: "/video", icon: <FileVideo size={16} /> },
      { label: "Subtitle Studio", path: "/subtitles", icon: <FileText size={16} /> },
      { label: "Processing Queue", path: "/processing", icon: <Cpu size={16} /> },
      { label: "Subtitle Presets", path: "/presets", icon: <BookOpen size={16} /> },
    ],
  },
  {
    label: "Review & Output",
    items: [
      { label: "Review Center", path: "/review", icon: <ListChecks size={16} /> },
      { label: "Approval History", path: "/approvals", icon: <CheckSquare size={16} /> },
      { label: "Drive Exports", path: "/drive-exports", icon: <HardDrive size={16} /> },
      { label: "Publishing Prep", path: "/publishing", icon: <Share2 size={16} /> },
      { label: "Manual Logs", path: "/manual-logs", icon: <History size={16} /> },
    ],
  },
  {
    label: "Insights",
    items: [
      { label: "App Analytics", path: "/analytics", icon: <BarChart3 size={16} /> },
      { label: "Social Analytics", path: "/analytics?tab=social", icon: <BarChart3 size={16} /> },
    ],
  },
  {
    label: "System",
    items: [
      { label: "Activity Log", path: "/activity", icon: <Activity size={16} /> },
      { label: "Settings", path: "/settings", icon: <Settings size={16} /> },
    ],
  },
];

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  onNavigate?: () => void;
}

export function Sidebar({ collapsed, onToggleCollapse, onNavigate }: SidebarProps) {
  const navigate = useNavigate();

  return (
    <aside
      className={cn(
        "h-full bg-surface border-r border-border flex flex-col transition-all duration-200 flex-shrink-0",
        collapsed ? "w-[60px]" : "w-[250px]"
      )}
    >
      <div className={cn("flex items-center gap-2.5 p-4 border-b border-border", collapsed && "justify-center")}>
        <Logo size={32} />
        {!collapsed && (
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-text-main truncate">Narrativ Forge</div>
            <div className="text-[10px] text-text-muted truncate">Burmese Short-Form Video Studio</div>
          </div>
        )}
      </div>

      {!collapsed && (
        <div className="px-4 py-2">
          <span className="text-[9px] font-mono tracking-wider text-text-muted uppercase">LOGIXA Ecosystem</span>
          <div className="mt-1">
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-medium bg-primary/15 text-primary border border-primary/20">
              PRIVATE WORKSPACE
            </span>
          </div>
        </div>
      )}

      <nav className="flex-1 overflow-y-auto px-2 py-2 space-y-3">
        {navGroups.map((group) => (
          <div key={group.label}>
            {!collapsed && (
              <div className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-text-muted">
                {group.label}
              </div>
            )}
            <div className="space-y-0.5">
              {group.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={onNavigate}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-2.5 px-2 py-1.5 rounded-md text-sm transition-colors",
                      collapsed && "justify-center",
                      isActive
                        ? "bg-primary/15 text-primary"
                        : "text-text-sec hover:bg-elevated hover:text-text-main"
                    )
                  }
                  title={collapsed ? item.label : undefined}
                >
                  {item.icon}
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-border p-3 space-y-2">
        {!collapsed && (
          <>
            <div className="flex items-center gap-2 text-[10px] text-text-muted">
              <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
              <span>UI Prototype — Local Mode</span>
            </div>
            <div className="flex items-center gap-2 text-[10px] text-text-muted">
              <Database size={10} />
              <span>Mock Storage: 42% used</span>
            </div>
            <div className="flex items-center gap-2 pt-2 border-t border-border-soft">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
                MM
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium text-text-main truncate">Min Min Ei</div>
                <div className="text-[10px] text-text-muted truncate">Owner</div>
              </div>
              <button onClick={() => navigate("/login")} className="icon-btn !w-6 !h-6" title="Sign out">
                <MoreVertical size={14} />
              </button>
            </div>
          </>
        )}
        <button
          onClick={onToggleCollapse}
          className={cn("flex items-center justify-center w-full py-1.5 rounded-md text-text-muted hover:bg-elevated hover:text-text-main transition-colors", collapsed && "mx-auto")}
        >
          <ChevronLeft size={16} className={cn("transition-transform", collapsed && "rotate-180")} />
        </button>
      </div>
    </aside>
  );
}
