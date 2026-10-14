import { expect, test } from "@playwright/test";

test("Series Bible characters persist after reload and can be removed", async ({ page }) => {
  const email = process.env.E2E_ADMIN_EMAIL;
  const password = process.env.E2E_ADMIN_PASSWORD;
  if (!email || !password) {
    test.skip(true, "E2E_ADMIN_EMAIL and E2E_ADMIN_PASSWORD are required for authenticated Series Bible UI coverage");
  }

  await page.goto("/login");
  await page.getByLabel("Email").fill(email!);
  await page.getByLabel("Password").fill(password!);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/dashboard/);

  const suffix = Date.now().toString();
  const seriesTitle = `Series Bible E2E ${suffix}`;
  await page.goto("/series");
  await page.getByPlaceholder("Series title").fill(seriesTitle);
  await page.getByRole("button", { name: "Create series" }).click();

  const seriesLink = page.getByRole("link", { name: new RegExp(seriesTitle) });
  await expect(seriesLink).toBeVisible();
  await seriesLink.click();
  await expect(page.getByText("Character Voice & Style Bible")).toBeVisible();

  const characterName = `E2E Character ${suffix}`;
  await page.getByPlaceholder("Character name (e.g. ဇေယျာ)").fill(characterName);
  await page.getByPlaceholder("Voice tone (e.g. Serious, playful, confident)").fill("Curious and warm");
  await page.getByPlaceholder("Catchphrase (မြန်မာစကားထာ/အသုံးအနှုန်း)").fill("မင်္ဂလာပါ");
  await page.getByRole("button", { name: "Save Character" }).click();

  const characterCard = page.locator("article.list-card").filter({ hasText: characterName });
  await expect(characterCard).toBeVisible();
  await expect(characterCard).toContainText("Curious and warm");

  await page.reload();
  await expect(page.getByText("Character Voice & Style Bible")).toBeVisible();
  const persistedCard = page.locator("article.list-card").filter({ hasText: characterName });
  await expect(persistedCard).toBeVisible();
  await expect(persistedCard).toContainText("မင်္ဂလာပါ");

  await persistedCard.getByRole("button").click();
  await expect(page.locator("article.list-card").filter({ hasText: characterName })).toHaveCount(0);
});
