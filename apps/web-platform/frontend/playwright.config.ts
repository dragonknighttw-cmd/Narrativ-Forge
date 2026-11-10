import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  use: {
    baseURL: "http://localhost:3000",
    // Cookie-authenticated API writes require a trusted browser Origin.
    extraHTTPHeaders: { Origin: process.env.E2E_FRONTEND_ORIGIN ?? "http://localhost:3000" },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  reporter: [["list"]],
});
