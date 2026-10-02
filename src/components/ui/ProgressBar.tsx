import React from "react";
import { cn } from "../../lib/utils";

export function ProgressBar({ value, className, color = "primary" }: { value: number; className?: string; color?: "primary" | "secondary" | "success" | "amber" | "error" }) {
  const colors: Record<string, string> = {
    primary: "bg-primary",
    secondary: "bg-secondary",
    success: "bg-success",
    amber: "bg-amber",
    error: "bg-error",
  };
  return (
    <div className={cn("h-1.5 bg-elevated rounded-full overflow-hidden", className)}>
      <div
        className={cn("h-full rounded-full transition-all duration-500", colors[color])}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  );
}
