import { expect, test } from "@playwright/test";

test("authenticated workspace UI routes use real API data and accessible mobile navigation", async ({ page }) => {
  const adminEmail = process.env.E2E_ADMIN_EMAIL;
  const adminPassword = process.env.E2E_ADMIN_PASSWORD;
  if (!adminEmail || !adminPassword) {
    throw new Error("E2E_ADMIN_EMAIL and E2E_ADMIN_PASSWORD must be set");
  }

  await page.goto("/login");
  await page.getByLabel("Email").fill(adminEmail);
  await page.getByLabel("Password").fill(adminPassword);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/dashboard/);

  // Exercise the mobile navigation at a real phone-sized viewport.
  await page.setViewportSize({ width: 390, height: 844 });
  const openNavigation = page.getByRole("button", { name: "Open navigation" });
  await expect(openNavigation).toBeVisible();
  await openNavigation.click();
  const drawer = page.getByRole("complementary", { name: "Mobile workspace navigation" });
  await expect(drawer).toBeVisible();
  await expect(drawer.getByRole("link", { name: "Dashboard" })).toHaveAttribute("aria-current", "page");
  await drawer.getByRole("link", { name: "Ideas" }).click();
  await expect(page).toHaveURL(/\/ideas$/);
  await expect(page.getByRole("button", { name: "Open navigation" })).toBeVisible();

  // Manual log and analytics must call the API host, not the Next.js frontend origin.
  const manualLogsResponsePromise = page.waitForResponse((response) =>
    new URL(response.url()).pathname.endsWith("/manual-production-logs")
    && response.request().method() === "GET",
  );
  await page.goto("/manual-log");
  const manualLogsResponse = await manualLogsResponsePromise;
  expect(manualLogsResponse.ok()).toBeTruthy();
  expect(manualLogsResponse.headers()["content-type"]).toContain("application/json");
  await expect(page.getByRole("heading", { name: "Production entries" })).toBeVisible();
  await expect(page.getByText(/Unexpected token/i)).toHaveCount(0);

  const analyticsResponsePromise = page.waitForResponse((response) =>
    new URL(response.url()).pathname.endsWith("/analytics")
    && response.request().method() === "GET",
  );
  await page.goto("/analytics");
  const analyticsResponse = await analyticsResponsePromise;
  expect(analyticsResponse.ok()).toBeTruthy();
  expect(analyticsResponse.headers()["content-type"]).toContain("application/json");
  await expect(page.getByRole("heading", { name: "Understand what is working." })).toBeVisible();
  await expect(page.getByText(/Unexpected token/i)).toHaveCount(0);

  await page.goto("/settings");
  await expect(page.getByRole("heading", { name: "Account details" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Workspace profile" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Service status" })).toBeVisible();

  await page.goto("/subtitle-presets");
  await expect(page.getByRole("button", { name: /Burmese Default/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /Burmese Compact/ })).toBeVisible();
  await expect(page.getByText(/No synthetic or estimated metrics/i)).toHaveCount(0);

  await page.goto("/recap");
  await expect(page.getByRole("heading", { name: "Shape the story before you cut the film." })).toBeVisible();
  await expect(page.getByText(/template-based script draft/i)).toBeVisible();
  await expect(page.getByRole("button", { name: "Preview edit plan" })).toBeDisabled();
});
