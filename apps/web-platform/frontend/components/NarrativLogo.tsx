import React from 'react';

interface LogoProps {
  className?: string;
  size?: number;
  showText?: boolean;
}

export function NarrativLogo({
  className = '',
  size = 40,
  showText = true,
}: LogoProps) {
  return (
    <div className={`flex items-center gap-3 select-none ${className}`}>
      {/* Clean Cinematic Shutter Tile */}
      <img
        src="/logo.svg"
        alt="Narrativ Forge Icon"
        width={size}
        height={size}
        className="shrink-0 object-contain rounded-2xl drop-shadow-[0_0_12px_rgba(245,158,11,0.25)] transition-transform duration-200 hover:scale-105"
      />

      {showText && (
        <div className="flex flex-col leading-none">
          <span className="text-[16px] font-bold tracking-tight text-white">
            Narrativ Forge
          </span>
          <span className="mt-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
            Cinematic Studio
          </span>
        </div>
      )}
    </div>
  );
}

export default NarrativLogo;
