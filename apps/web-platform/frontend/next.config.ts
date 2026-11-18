import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Package as standalone for portable / Render node server; Vercel handles its own output
  output: process.env.VERCEL ? undefined : "standalone",
  env: {
    // API base URL — override via NEXT_PUBLIC_API_BASE_URL env var in Vercel/Render dashboard
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://narrativ-forge.onrender.com/api/v1",
    // Supabase — MUST be set in Vercel/Render env dashboard; no hardcoded fallback in production
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL ?? "",
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "",
    NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? "",
  },
};

export default nextConfig;
