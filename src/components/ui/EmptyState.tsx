import React from "react";
import { cn } from "../../lib/utils";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 px-4 text-center", className)}>
      <div className="w-12 h-12 rounded-xl bg-elevated border border-border flex items-center justify-center text-text-muted mb-4">
        {icon || <Inbox size={20} />}
      </div>
      <h3 className="text-base font-semibold text-text-main mb-1">{title}</h3>
      {description && <p className="text-sm text-text-muted max-w-sm mb-4">{description}</p>}
      {action}
    </div>
  );
}

export function LoadingSkeleton({ className, rows = 3 }: { className?: string; rows?: number }) {
  return (
    <div className={cn("space-y-3", className)}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton h-12" />
      ))}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <div className="w-12 h-12 rounded-xl bg-error/15 border border-error/30 flex items-center justify-center text-error mb-4">
        <span className="text-lg">!</span>
      </div>
      <h3 className="text-base font-semibold text-text-main mb-1">Something went wrong</h3>
      <p className="text-sm text-text-muted max-w-sm mb-4">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary text-sm">Retry</button>
      )}
    </div>
  );
}
