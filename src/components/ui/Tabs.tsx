import React from "react";
import { cn } from "../../lib/utils";

interface Tab {
  label: string;
  value: string;
  icon?: React.ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  active: string;
  onChange: (value: string) => void;
  className?: string;
}

export function Tabs({ tabs, active, onChange, className }: TabsProps) {
  return (
    <div className={cn("flex items-center gap-1 border-b border-border overflow-x-auto", className)}>
      {tabs.map((tab) => (
        <button
          key={tab.value}
          onClick={() => onChange(tab.value)}
          className={cn(
            "flex items-center gap-2 px-3 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap",
            active === tab.value
              ? "border-primary text-text-main"
              : "border-transparent text-text-muted hover:text-text-sec"
          )}
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  );
}
