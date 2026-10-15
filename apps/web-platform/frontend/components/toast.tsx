"use client";

import React, { useEffect, useState } from "react";

export type ToastType = "success" | "error" | "info" | "warning";

export interface ToastItem {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
  duration?: number;
}

type Listener = (toast: ToastItem) => void;
const listeners: Listener[] = [];

export const toast = {
  success: (message: string, title?: string, duration = 4000) => {
    emit({ id: Math.random().toString(36).slice(2), type: "success", title, message, duration });
  },
  error: (message: string, title?: string, duration = 5000) => {
    emit({ id: Math.random().toString(36).slice(2), type: "error", title, message, duration });
  },
  info: (message: string, title?: string, duration = 4000) => {
    emit({ id: Math.random().toString(36).slice(2), type: "info", title, message, duration });
  },
  warning: (message: string, title?: string, duration = 4000) => {
    emit({ id: Math.random().toString(36).slice(2), type: "warning", title, message, duration });
  },
};

function emit(toast: ToastItem) {
  listeners.forEach((fn) => fn(toast));
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  useEffect(() => {
    const handleToast = (newToast: ToastItem) => {
      setToasts((prev) => [...prev, newToast]);
    };
    listeners.push(handleToast);
    return () => {
      const idx = listeners.indexOf(handleToast);
      if (idx !== -1) listeners.splice(idx, 1);
    };
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div
      style={{
        position: "fixed",
        bottom: "20px",
        right: "20px",
        zIndex: 9999,
        display: "flex",
        flexDirection: "column",
        gap: "10px",
        maxWidth: "380px",
        pointerEvents: "none",
      }}
    >
      {toasts.map((t) => (
        <ToastCard key={t.id} toast={t} onClose={() => removeToast(t.id)} />
      ))}
    </div>
  );
}

function ToastCard({ toast, onClose }: { toast: ToastItem; onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onClose, toast.duration || 4000);
    return () => clearTimeout(timer);
  }, [toast, onClose]);

  const styles = {
    success: {
      bg: "#061812",
      border: "1px solid rgba(16, 185, 129, 0.35)",
      color: "#34d399",
      icon: "✓",
    },
    error: {
      bg: "#1c0910",
      border: "1px solid rgba(244, 63, 94, 0.35)",
      color: "#fb7185",
      icon: "✕",
    },
    warning: {
      bg: "#1c1407",
      border: "1px solid rgba(245, 158, 11, 0.35)",
      color: "#fbbf24",
      icon: "⚠️",
    },
    info: {
      bg: "#0b1424",
      border: "1px solid rgba(56, 189, 248, 0.35)",
      color: "#38bdf8",
      icon: "ℹ",
    },
  }[toast.type];

  return (
    <div
      style={{
        pointerEvents: "auto",
        backgroundColor: styles.bg,
        border: styles.border,
        borderRadius: "12px",
        padding: "12px 16px",
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.4)",
        display: "flex",
        alignItems: "flex-start",
        gap: "12px",
        animation: "slideIn 0.25s ease-out",
      }}
    >
      <span style={{ fontSize: "14px", fontWeight: "bold", color: styles.color, marginTop: "2px" }}>
        {styles.icon}
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        {toast.title && (
          <div style={{ fontSize: "13px", fontWeight: 600, color: styles.color, marginBottom: "2px" }}>
            {toast.title}
          </div>
        )}
        <div style={{ fontSize: "12px", color: "#e2e8f0", lineHeight: 1.4 }}>{toast.message}</div>
      </div>
      <button
        type="button"
        onClick={onClose}
        style={{
          background: "transparent",
          border: "none",
          color: "#94a3b8",
          fontSize: "14px",
          cursor: "pointer",
          padding: "0 4px",
          lineHeight: 1,
        }}
      >
        ×
      </button>
    </div>
  );
}
