import React from "react";
import { cn } from "../../lib/utils";
import { getStatusColor } from "../../lib/constants";

interface BadgeProps {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "primary" | "secondary" | "success" | "warning" | "error" | "amber";
}

export function Badge({ children, className, variant = "default" }: BadgeProps) {
  const variants: Record<string, string> = {
    default: "bg-elevated text-text-sec border-border",
    primary: "bg-primary/15 text-primary border-primary/30",
    secondary: "bg-secondary/15 text-secondary border-secondary/30",
    success: "bg-success/15 text-success border-success/30",
    warning: "bg-warning/15 text-warning border-warning/30",
    error: "bg-error/15 text-error border-error/30",
    amber: "bg-amber/15 text-amber border-amber/30",
  };
  return (
    <span className={cn("inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-xs font-medium border", variants[variant], className)}>
      {children}
    </span>
  );
}

interface StatusBadgeProps {
  status: string;
  showDot?: boolean;
  className?: string;
}

export function StatusBadge({ status, showDot = true, className }: StatusBadgeProps) {
  const colors = getStatusColor(status);
  return (
    <span className={cn("inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-xs font-medium border whitespace-nowrap", colors.bg, colors.text, colors.border, className)}>
      {showDot && <span className={cn("w-1.5 h-1.5 rounded-full", colors.dot)} />}
      {status}
    </span>
  );
}
