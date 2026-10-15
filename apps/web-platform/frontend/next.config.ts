import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Package the existing UI as a portable Node server; the local API URL is
  // injected at build time by the Windows portable-runtime workflow.
  output: "standalone",
};

export default nextConfig;
