import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Package as standalone for portable / Render node server; Vercel handles its own output
  output: process.env.VERCEL ? undefined : "standalone",
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || "https://narrativ-forge.onrender.com/api/v1",
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL || "https://xrhlefglqwquhvpoevsg.supabase.co",
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "sb_publishable_INLd5Okf76u-oATKOpPQcQ_bPjPlhFr",
    NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || "sb_publishable_INLd5Okf76u-oATKOpPQcQ_bPjPlhFr",
  },
};

export default nextConfig;
