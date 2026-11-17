import React from 'react';

interface LogoProps {
  className?: string;
  size?: number;
  showText?: boolean;
}

export function NarrativLogo({
  className = '',
  size = 38,
  showText = true,
}: LogoProps) {
  return (
    <div
      className={`nf-logo-container ${className}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        userSelect: 'none',
      }}
    >
      {/* Clean Cinematic Shutter Tile */}
      <img
        src="/logo.svg"
        alt="Narrativ Forge Icon"
        width={size}
        height={size}
        style={{
          width: `${size}px`,
          height: `${size}px`,
          flexShrink: 0,
          objectFit: 'contain',
          borderRadius: '10px',
          filter: 'drop-shadow(0 0 10px rgba(216, 255, 79, 0.25))',
        }}
      />

      {showText && (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            lineHeight: 1.15,
            minWidth: 0,
          }}
        >
          <div
            style={{
              fontSize: '15px',
              fontWeight: 800,
              letterSpacing: '-0.02em',
              color: '#f4f7f8',
              whiteSpace: 'nowrap',
            }}
          >
            Narrativ Forge
          </div>
          <div
            style={{
              fontSize: '10px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.14em',
              color: '#d8ff4f',
              marginTop: '2px',
              whiteSpace: 'nowrap',
            }}
          >
            Cinematic Studio
          </div>
        </div>
      )}
    </div>
  );
}

export default NarrativLogo;
