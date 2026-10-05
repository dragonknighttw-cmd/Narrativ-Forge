import { test, expect, request as playwrightRequest } from "@playwright/test";

const apiBase = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const ownerEmail = process.env.E2E_EMAIL;
const ownerPassword = process.env.E2E_PASSWORD;

test.describe("Cross-tenant isolation", () => {
  test.skip(!ownerEmail || !ownerPassword, "Set E2E_EMAIL and E2E_PASSWORD to run authenticated E2E coverage");

  test("workspace resources cannot cross tenant boundaries", async ({ request }) => {
    const ownerLogin = await request.post(`${apiBase}/auth/login`, {
      data: { email: ownerEmail, password: ownerPassword },
    });
    expect(ownerLogin.ok()).toBeTruthy();

    const suffix = Date.now();
    const secondEmail = `e2e-tenant-${suffix}@example.test`;
    const secondPassword = process.env.E2E_SECOND_PASSWORD ?? "E2e-Second-Password-ChangeMe1!";
    const invite = await request.post(`${apiBase}/auth/invite`, {
      data: { email: secondEmail, password: secondPassword, role: "owner" },
    });
    expect(invite.ok()).toBeTruthy();

    const series = await request.post(`${apiBase}/series`, {
      data: { title: `Tenant A ${suffix}` },
    });
    expect(series.ok()).toBeTruthy();
    const seriesId = (await series.json()).id;

    const tag = await request.post(`${apiBase}/phase4/tags`, {
      data: { name: `tenant-a-${suffix}` },
    });
    expect(tag.ok()).toBeTruthy();
    const tagId = (await tag.json()).id;

    const secondContext = await playwrightRequest.newContext();
    try {
      const secondLogin = await secondContext.post(`${apiBase}/auth/login`, {
        data: { email: secondEmail, password: secondPassword },
      });
      expect(secondLogin.ok()).toBeTruthy();

      const secondWorkspace = await secondContext.get(`${apiBase}/phase4/workspace`);
      expect(secondWorkspace.ok()).toBeTruthy();
      expect((await secondWorkspace.json()).id).not.toBe((await request.get(`${apiBase}/phase4/workspace`).then(r => r.json())).id);

      const hiddenSeries = await secondContext.get(`${apiBase}/series/${seriesId}`);
      expect(hiddenSeries.status()).toBe(404);

      const secondTags = await secondContext.get(`${apiBase}/phase4/tags`);
      expect(secondTags.ok()).toBeTruthy();
      expect((await secondTags.json()).some((item: { id: string }) => item.id === tagId)).toBeFalsy();

      const crossTenantAssignment = await secondContext.post(`${apiBase}/phase4/tags/${tagId}/assign`, {
        data: { resource_type: "series", resource_id: seriesId },
      });
      expect(crossTenantAssignment.status()).toBe(404);
    } finally {
      await secondContext.dispose();
    }
  });
});
