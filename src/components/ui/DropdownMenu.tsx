import React, { useRef, useState, useEffect } from "react";
import { cn } from "../../lib/utils";

interface DropdownItem {
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  danger?: boolean;
  separator?: boolean;
}

interface DropdownMenuProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  align?: "left" | "right";
}

export function DropdownMenu({ trigger, items, align = "right" }: DropdownMenuProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <div onClick={() => setOpen(!open)}>{trigger}</div>
      {open && (
        <div
          className={cn(
            "absolute top-full mt-1 z-50 bg-elevated border border-border rounded-lg shadow-xl py-1 min-w-[180px] animate-fade-in",
            align === "right" ? "right-0" : "left-0"
          )}
        >
          {items.map((item, i) => (
            <React.Fragment key={i}>
              {item.separator && <div className="h-px bg-border my-1" />}
              <button
                onClick={() => {
                  item.onClick();
                  setOpen(false);
                }}
                className={cn(
                  "w-full flex items-center gap-2.5 px-3 py-2 text-sm text-left transition-colors hover:bg-surface",
                  item.danger ? "text-error hover:bg-error/10" : "text-text-sec hover:text-text-main"
                )}
              >
                {item.icon}
                {item.label}
              </button>
            </React.Fragment>
          ))}
        </div>
      )}
    </div>
  );
}
