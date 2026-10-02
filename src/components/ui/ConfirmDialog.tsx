import React, { useEffect, useState } from "react";
import { cn } from "../../lib/utils";

interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
}

export function ConfirmDialog({ open, onClose, onConfirm, title, message, confirmLabel = "Confirm", danger = false }: ConfirmDialogProps) {
  useEffect(() => {
    if (open) {
      const handleEsc = (e: KeyboardEvent) => e.key === "Escape" && onClose();
      window.addEventListener("keydown", handleEsc);
      return () => window.removeEventListener("keydown", handleEsc);
    }
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 animate-fade-in" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-bg/80 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-sm bg-surface border border-border rounded-lg shadow-2xl animate-slide-up p-5">
        <h3 className="text-base font-semibold text-text-main mb-2">{title}</h3>
        <p className="text-sm text-text-muted mb-5">{message}</p>
        <div className="flex items-center justify-end gap-2">
          <button onClick={onClose} className="btn-ghost text-sm">Cancel</button>
          <button
            onClick={() => { onConfirm(); onClose(); }}
            className={cn("text-sm", danger ? "btn-danger" : "btn-primary")}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
