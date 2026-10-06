import { test, expect } from "@playwright/test";

const apiBase = process.env.E2E_API_BASE_URL ?? "http://localhost:8000/api/v1";
const email = process.env.E2E_EMAIL;
const password = process.env.E2E_PASSWORD;

test.describe("Phase 4 foundation", () => {
  test.skip(!email || !password, "Set E2E_EMAIL and E2E_PASSWORD to run authenticated E2E coverage");

  test("login → tenant workspace → tags → usage → billing → webhook", async ({ request }) => {
    const login = await request.post(`${apiBase}/auth/login`, { data: { email, password } });
    expect(login.ok()).toBeTruthy();
    const workspace = await request.get(`${apiBase}/phase4/workspace`);
    expect(workspace.ok()).toBeTruthy();
    const workspaceBody = await workspace.json();
    expect(workspaceBody.id).toBeTruthy();

    const tag = await request.post(`${apiBase}/phase4/tags`, { data: { name: `e2e-${Date.now()}` } });
    expect(tag.ok()).toBeTruthy();
    expect((await tag.json()).id).toBeTruthy();

    const usage = await request.post(`${apiBase}/phase4/usage`, {
      data: { metric: "e2e_processing_minutes", quantity: 1, unit: "minute", idempotency_key: `e2e-${Date.now()}` },
    });
    expect(usage.ok()).toBeTruthy();
    const summary = await request.get(`${apiBase}/phase4/usage`);
    expect(summary.ok()).toBeTruthy();
    expect((await summary.json()).totals.e2e_processing_minutes).toBeGreaterThanOrEqual(1);

    const billing = await request.get(`${apiBase}/phase4/billing`);
    expect(billing.ok()).toBeTruthy();
    expect((await billing.json()).plan).toBeTruthy();

    const webhook = await request.post(`${apiBase}/phase4/webhooks`, {
      data: { url: "https://example.invalid/narrativ-forge", events: ["e2e.test"] },
    });
    expect(webhook.ok()).toBeTruthy();
    expect((await webhook.json()).secret).toBeTruthy();
  });
});
