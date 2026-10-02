import React, { useEffect } from "react";
import { cn } from "../../lib/utils";
import { X } from "lucide-react";

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  side?: "right" | "bottom";
  width?: string;
}

export function Drawer({ open, onClose, title, children, side = "right", width = "400px" }: DrawerProps) {
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
      const handleEsc = (e: KeyboardEvent) => e.key === "Escape" && onClose();
      window.addEventListener("keydown", handleEsc);
      return () => {
        document.body.style.overflow = "";
        window.removeEventListener("keydown", handleEsc);
      };
    }
  }, [open, onClose]);

  if (!open) return null;

  if (side === "bottom") {
    return (
      <div className="fixed inset-0 z-50 flex items-end justify-center animate-fade-in" role="dialog" aria-modal="true">
        <div className="absolute inset-0 bg-bg/80 backdrop-blur-sm" onClick={onClose} />
        <div className="relative w-full bg-surface border border-border rounded-t-lg shadow-2xl animate-slide-up max-h-[85vh] flex flex-col">
          {title && (
            <div className="flex items-center justify-between p-4 border-b border-border">
              <h2 className="text-base font-semibold text-text-main">{title}</h2>
              <button onClick={onClose} className="text-text-muted hover:text-text-main transition-colors p-1">
                <X size={18} />
              </button>
            </div>
          )}
          <div className="p-4 overflow-y-auto">{children}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end animate-fade-in" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-bg/80 backdrop-blur-sm" onClick={onClose} />
      <div
        className="relative h-full bg-surface border-l border-border shadow-2xl animate-slide-right flex flex-col overflow-hidden"
        style={{ width: `min(${width}, 100vw)` }}
      >
        {title && (
          <div className="flex items-center justify-between p-4 border-b border-border flex-shrink-0">
            <h2 className="text-base font-semibold text-text-main">{title}</h2>
            <button onClick={onClose} className="text-text-muted hover:text-text-main transition-colors p-1">
              <X size={18} />
            </button>
          </div>
        )}
        <div className="p-4 overflow-y-auto flex-1">{children}</div>
      </div>
    </div>
  );
}
