/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#090A12",
        surface: "#121321",
        elevated: "#1A1B2C",
        border: "#303249",
        "border-soft": "#232539",
        primary: "#8B7CFF",
        "primary-dim": "#6B5FCC",
        secondary: "#4BC7E8",
        "secondary-dim": "#3A9DB8",
        amber: "#F1B75B",
        success: "#42C98A",
        warning: "#F0B84E",
        error: "#F16F79",
        "text-main": "#F7F5FA",
        "text-sec": "#B5B2C2",
        "text-muted": "#7D7B8F",
      },
      fontFamily: {
        sans: ["Inter", "Plus Jakarta Sans", "Geist", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
        burmese: ["Padauk", "Noto Sans Myanmar", "Inter", "sans-serif"],
      },
      spacing: {
        1: "4px",
        2: "8px",
        3: "12px",
        4: "16px",
        5: "20px",
        6: "24px",
        8: "32px",
        10: "40px",
        12: "48px",
      },
      borderRadius: {
        sm: "4px",
        md: "8px",
        lg: "12px",
        xl: "16px",
      },
      animation: {
        "fade-in": "fadeIn 200ms ease-out",
        "slide-up": "slideUp 250ms ease-out",
        "slide-right": "slideRight 250ms ease-out",
        "shimmer": "shimmer 1.5s infinite linear",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideRight: {
          "0%": { opacity: "0", transform: "translateX(-8px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};
