import React from "react";
import { cn } from "../../lib/utils";
import { Check } from "lucide-react";

interface Step {
  label: string;
  done: boolean;
  current?: boolean;
}

export function Stepper({ steps, className }: { steps: Step[]; className?: string }) {
  return (
    <div className={cn("flex items-center gap-1 overflow-x-auto", className)}>
      {steps.map((step, i) => (
        <React.Fragment key={i}>
          <div className="flex items-center gap-1.5 flex-shrink-0">
            <div
              className={cn(
                "w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-semibold border transition-colors",
                step.done
                  ? "bg-success/20 text-success border-success/40"
                  : step.current
                  ? "bg-primary/20 text-primary border-primary/40 animate-pulse"
                  : "bg-elevated text-text-muted border-border"
              )}
            >
              {step.done ? <Check size={10} /> : i + 1}
            </div>
            <span
              className={cn(
                "text-xs whitespace-nowrap",
                step.done ? "text-text-sec" : step.current ? "text-text-main font-medium" : "text-text-muted"
              )}
            >
              {step.label}
            </span>
          </div>
          {i < steps.length - 1 && (
            <div className={cn("h-px flex-shrink-0", step.done ? "bg-success/30" : "bg-border", "w-4")} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
