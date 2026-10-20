import React from "react";

interface LogoProps {
  className?: string;
  size?: number;
  showText?: boolean;
}

export function NarrativLogo({ className = "", size = 34, showText = true }: LogoProps) {
  return (
    <div className={`flex items-center gap-2.5 select-none ${className}`}>
      {/* High-Tech Shutter Flame & Anvil SVG Icon */}
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0 transition-transform hover:scale-105 duration-300"
      >
        <defs>
          <linearGradient id="nf-flame-grad" x1="4" y1="44" x2="44" y2="4" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#DC2626" />
            <stop offset="45%" stopColor="#F59E0B" />
            <stop offset="100%" stopColor="#FDE047" />
          </linearGradient>
          <linearGradient id="nf-shutter-grad" x1="10" y1="10" x2="38" y2="38" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#F59E0B" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#B45309" stopOpacity="0.4" />
          </linearGradient>
          <filter id="nf-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Outer Dark Forge Shield with subtle gold stroke */}
        <rect
          x="3"
          y="3"
          width="42"
          height="42"
          rx="12"
          fill="#0c101c"
          stroke="url(#nf-flame-grad)"
          strokeWidth="1.75"
        />

        {/* Cinematic Aperture / Shutter Blades (Geometry of Stories) */}
        <g filter="url(#nf-glow)">
          {/* Top Blade */}
          <path d="M14 12H34L26 21H14V12Z" fill="url(#nf-shutter-grad)" opacity="0.8" />
          {/* Right Blade */}
          <path d="M36 14V34L27 26V14H36Z" fill="url(#nf-shutter-grad)" opacity="0.85" />
          {/* Bottom Blade */}
          <path d="M34 36H14L22 27H34V36Z" fill="url(#nf-shutter-grad)" opacity="0.9" />
          {/* Left Blade */}
          <path d="M12 34V14L21 22V34H12Z" fill="url(#nf-shutter-grad)" opacity="0.75" />
        </g>

        {/* Central Stylized "N" & Play Spear in Glowing Flame Gradient */}
        <path
          d="M17 33V15L29 29V15"
          stroke="url(#nf-flame-grad)"
          strokeWidth="3.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Play Spark Accent (Movie Beat Dot) */}
        <circle cx="33" cy="33" r="2.5" fill="#FDE047" className="animate-pulse" />
      </svg>

      {showText && (
        <div className="flex flex-col leading-none">
          <span className="text-[15px] font-black tracking-tight text-white flex items-center gap-1.5">
            NARRATIV<span className="bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">FORGE</span>
          </span>
          <span className="text-[9px] font-semibold uppercase tracking-[0.22em] text-amber-500/80 mt-0.5">
            Cinematic AI Studio
          </span>
        </div>
      )}
    </div>
  );
}
export default NarrativLogo;
