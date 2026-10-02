import React from "react";

export function Logo({ size = 32 }: { size?: number }) {
  return (
    <div
      className="flex items-center justify-center rounded-lg bg-gradient-to-br from-primary to-secondary"
      style={{ width: size, height: size }}
    >
      <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 3h18v18H3z" opacity="0.2" fill="white" />
        <path d="M7 7v10M12 7v10M17 7v10" />
        <circle cx="7" cy="9" r="1" fill="white" stroke="none" />
        <circle cx="12" cy="13" r="1" fill="white" stroke="none" />
        <circle cx="17" cy="11" r="1" fill="white" stroke="none" />
      </svg>
    </div>
  );
}
