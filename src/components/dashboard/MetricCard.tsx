import React from "react";
import { cn } from "../lib/utils";
import { TrendingUp, TrendingDown } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  change?: { value: string; positive: boolean };
  color?: "primary" | "secondary" | "amber" | "success" | "error";
  onClick?: () => void;
}

export function MetricCard({ label, value, icon, change, color = "primary", onClick }: MetricCardProps) {
  const colors: Record<string, { bg: string; text: string; border: string }> = {
    primary: { bg: "bg-primary/10", text: "text-primary", border: "border-primary/20" },
    secondary: { bg: "bg-secondary/10", text: "text-secondary", border: "border-secondary/20" },
    amber: { bg: "bg-amber/10", text: "text-amber", border: "border-amber/20" },
    success: { bg: "bg-success/10", text: "text-success", border: "border-success/20" },
    error: { bg: "bg-error/10", text: "text-error", border: "border-error/20" },
  };
  return (
    <div
      onClick={onClick}
      className={cn(
        "bg-surface border border-border rounded-lg p-4 transition-all",
        onClick && "cursor-pointer hover:border-primary/30 hover:bg-elevated"
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={cn("w-9 h-9 rounded-lg flex items-center justify-center border", colors[color].bg, colors[color].text, colors[color].border)}>
          {icon}
        </div>
        {change && (
          <div className={cn("flex items-center gap-1 text-[11px] font-medium", change.positive ? "text-success" : "text-error")}>
            {change.positive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {change.value}
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-text-main">{value}</div>
      <div className="text-xs text-text-muted mt-0.5">{label}</div>
    </div>
  );
}
