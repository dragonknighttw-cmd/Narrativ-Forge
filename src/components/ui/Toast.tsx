import React, { createContext, useContext, useState, useCallback } from "react";
import { CheckCircle2, AlertCircle, Info, X, XCircle } from "lucide-react";
import { cn } from "../../lib/utils";

type ToastType = "success" | "error" | "info" | "warning";

interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastContextValue {
  toast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback((message: string, type: ToastType = "success") => {
    const id = `toast_${Date.now()}_${Math.random()}`;
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  }, []);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const icons: Record<ToastType, React.ReactNode> = {
    success: <CheckCircle2 size={16} className="text-success" />,
    error: <XCircle size={16} className="text-error" />,
    info: <Info size={16} className="text-secondary" />,
    warning: <AlertCircle size={16} className="text-warning" />,
  };

  const borders: Record<ToastType, string> = {
    success: "border-success/30",
    error: "border-error/30",
    info: "border-secondary/30",
    warning: "border-warning/30",
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={cn("flex items-center gap-2.5 bg-elevated border rounded-lg px-4 py-3 shadow-xl animate-slide-up", borders[t.type])}
          >
            {icons[t.type]}
            <span className="text-sm text-text-main flex-1">{t.message}</span>
            <button onClick={() => dismiss(t.id)} className="text-text-muted hover:text-text-main">
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
