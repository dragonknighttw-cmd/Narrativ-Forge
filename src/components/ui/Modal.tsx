import React, { useEffect } from "react";
import { cn } from "../../lib/utils";
import { X } from "lucide-react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
}

export function Modal({ open, onClose, title, description, children, footer, size = "md" }: ModalProps) {
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

  const sizes: Record<string, string> = {
    sm: "max-w-md",
    md: "max-w-lg",
    lg: "max-w-2xl",
    xl: "max-w-4xl",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-bg/80 backdrop-blur-sm" onClick={onClose} />
      <div className={cn("relative w-full bg-surface border border-border rounded-lg shadow-2xl animate-slide-up max-h-[90vh] flex flex-col", sizes[size])}>
        {(title || description) && (
          <div className="flex items-start justify-between p-4 border-b border-border">
            <div>
              {title && <h2 className="text-base font-semibold text-text-main">{title}</h2>}
              {description && <p className="text-sm text-text-muted mt-1">{description}</p>}
            </div>
            <button onClick={onClose} className="text-text-muted hover:text-text-main transition-colors p-1">
              <X size={18} />
            </button>
          </div>
        )}
        <div className="p-4 overflow-y-auto flex-1">{children}</div>
        {footer && <div className="flex items-center justify-end gap-2 p-4 border-t border-border">{footer}</div>}
      </div>
    </div>
  );
}
