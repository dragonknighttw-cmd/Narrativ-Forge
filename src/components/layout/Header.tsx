import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { cn } from "../../lib/utils";
import {
  Search, Bell, Plus, Menu, Lightbulb, Film, Clapperboard,
  PenLine, FolderClosed, History, ChevronRight, X,
} from "lucide-react";
import { DropdownMenu } from "../ui/DropdownMenu";
import { Drawer } from "../ui/Drawer";
import { mockNotifications } from "../../lib/mock-data";

interface HeaderProps {
  onMenuClick: () => void;
  pageTitle: string;
  breadcrumb: { label: string; path?: string }[];
}

const createMenuItems = (navigate: (path: string) => void) => [
  { label: "New Idea", icon: <Lightbulb size={14} />, onClick: () => navigate("/ideas") },
  { label: "New Series", icon: <Film size={14} />, onClick: () => navigate("/series") },
  { label: "New Episode", icon: <Clapperboard size={14} />, onClick: () => navigate("/episodes") },
  { label: "New Script", icon: <PenLine size={14} />, onClick: () => navigate("/scripts") },
  { label: "Upload Asset", icon: <FolderClosed size={14} />, onClick: () => navigate("/assets") },
  { label: "New Manual Log", icon: <History size={14} />, onClick: () => navigate("/manual-logs") },
];

export function Header({ onMenuClick, pageTitle, breadcrumb }: HeaderProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchOpen, setSearchOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const searchRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (searchOpen && searchRef.current) {
      searchRef.current.focus();
    }
  }, [searchOpen]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
      if (e.key === "Escape") {
        setSearchOpen(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <>
      <header className="h-14 bg-surface border-b border-border flex items-center gap-3 px-4 flex-shrink-0 z-30">
        <button onClick={onMenuClick} className="lg:hidden icon-btn">
          <Menu size={20} />
        </button>

        <div className="flex items-center gap-1.5 text-sm min-w-0 flex-1">
          {breadcrumb.map((bc, i) => (
            <React.Fragment key={i}>
              {i > 0 && <ChevronRight size={12} className="text-text-muted flex-shrink-0" />}
              {bc.path ? (
                <button
                  onClick={() => navigate(bc.path!)}
                  className="text-text-muted hover:text-text-sec transition-colors truncate"
                >
                  {bc.label}
                </button>
              ) : (
                <span className={cn(i === breadcrumb.length - 1 ? "text-text-main font-medium" : "text-text-muted", "truncate")}>
                  {bc.label}
                </span>
              )}
            </React.Fragment>
          ))}
        </div>

        <button
          onClick={() => setSearchOpen(true)}
          className="hidden md:flex items-center gap-2 bg-elevated border border-border rounded-md px-3 py-1.5 text-sm text-text-muted hover:border-primary/40 transition-colors w-48"
        >
          <Search size={14} />
          <span className="text-xs">Search...</span>
          <kbd className="ml-auto text-[10px] font-mono bg-surface px-1.5 py-0.5 rounded border border-border">⌘K</kbd>
        </button>

        <button onClick={() => setSearchOpen(true)} className="md:hidden icon-btn">
          <Search size={18} />
        </button>

        <DropdownMenu
          trigger={
            <button className="btn-primary text-sm">
              <Plus size={16} />
              <span className="hidden sm:inline">Create</span>
            </button>
          }
          items={createMenuItems(navigate)}
        />

        <button onClick={() => setNotifOpen(true)} className="icon-btn relative">
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-error rounded-full" />
        </button>

        <div
          className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs font-semibold cursor-pointer flex-shrink-0"
          onClick={() => navigate("/settings")}
        >
          MM
        </div>
      </header>

      {searchOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] px-4 animate-fade-in" role="dialog" aria-modal="true">
          <div className="absolute inset-0 bg-bg/80 backdrop-blur-sm" onClick={() => setSearchOpen(false)} />
          <div className="relative w-full max-w-xl bg-surface border border-border rounded-lg shadow-2xl animate-slide-up overflow-hidden">
            <div className="flex items-center gap-3 p-4 border-b border-border">
              <Search size={18} className="text-text-muted" />
              <input
                ref={searchRef}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search episodes, series, ideas, assets..."
                className="flex-1 bg-transparent text-sm text-text-main placeholder:text-text-muted focus:outline-none"
              />
              <button onClick={() => setSearchOpen(false)} className="icon-btn">
                <X size={16} />
              </button>
            </div>
            <div className="max-h-[50vh] overflow-y-auto p-2">
              {[
                { label: "Episodes", path: "/episodes", icon: <Clapperboard size={14} /> },
                { label: "Content Ideas", path: "/ideas", icon: <Lightbulb size={14} /> },
                { label: "All Series", path: "/series", icon: <Film size={14} /> },
                { label: "Asset Library", path: "/assets", icon: <FolderClosed size={14} /> },
                { label: "Script Studio", path: "/scripts", icon: <PenLine size={14} /> },
                { label: "Manual Production Logs", path: "/manual-logs", icon: <History size={14} /> },
              ].map((item) => (
                <button
                  key={item.path}
                  onClick={() => { navigate(item.path); setSearchOpen(false); }}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm text-text-sec hover:bg-elevated hover:text-text-main transition-colors text-left"
                >
                  {item.icon}
                  <span>{searchQuery ? `Search "${searchQuery}" in ${item.label}` : item.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <Drawer open={notifOpen} onClose={() => setNotifOpen(false)} title="Notifications" width="380px">
        <div className="space-y-2">
          {mockNotifications.map((n) => (
            <div
              key={n.id}
              className={cn(
                "p-3 rounded-lg border cursor-pointer transition-colors hover:bg-elevated",
                n.read ? "bg-surface border-border" : "bg-primary/5 border-primary/20"
              )}
              onClick={() => { navigate(`/episodes/${n.episodeId}`); setNotifOpen(false); }}
            >
              <div className="flex items-start gap-3">
                <div className={cn(
                  "w-2 h-2 rounded-full mt-1.5 flex-shrink-0",
                  n.type === "error" ? "bg-error" : n.type === "warning" ? "bg-warning" : n.type === "success" ? "bg-success" : "bg-secondary"
                )} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-text-main">{n.title}</div>
                  <div className="text-xs text-text-muted mt-0.5">{n.message}</div>
                  <div className="text-[10px] text-text-muted mt-1">{n.time}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Drawer>
    </>
  );
}
