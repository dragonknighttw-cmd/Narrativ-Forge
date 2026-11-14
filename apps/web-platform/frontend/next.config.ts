import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Package as standalone for portable / Render node server; Vercel handles its own output
  output: process.env.VERCEL ? undefined : "standalone",
};

export default nextConfig;
