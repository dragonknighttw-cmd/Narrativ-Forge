import { expect, test } from "@playwright/test";

test("authenticated production flow reaches approved mock export", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("undefined");
  await page.getByLabel("Password").fill("change-me-123456");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/dashboard/);

  await page.goto("/series");
  await page.getByPlaceholder("Series title").fill("E2E Series");
  await page.getByRole("button", { name: "Create series" }).click();
  await expect(page.getByText("E2E Series")).toBeVisible();

  await page.goto("/episodes");
  await page.getByPlaceholder("Episode title").fill("E2E Episode");
  await page.getByRole("button", { name: "Create episode" }).click();
  await expect(page.getByText("E2E Episode")).toBeVisible();

  await page.getByRole("link", { name: /E2E Episode/ }).first().click();
  await expect(page.getByText("PRODUCTION WORKSPACES")).toBeVisible();

  const episodeId = new URL(page.url()).pathname.split("/").filter(Boolean).pop()!;
  const api = page.request;
  const apiBase = "http://127.0.0.1:8000/api/v1";

  const upload = await api.post(apiBase + "/episodes/" + episodeId + "/assets/upload", {
    multipart: {
      file: { name: "source.mp4", mimeType: "video/mp4", buffer: Buffer.from("video-fixture") },
      asset_type: "video",
      copyright_status: "licensed",
    },
  });
  expect(upload.ok()).toBeTruthy();

  const job = await api.post(apiBase + "/jobs/mock", { data: { episode_id: episodeId } });
  expect(job.ok()).toBeTruthy();

  const subtitle = await api.post(apiBase + "/episodes/" + episodeId + "/subtitles/generate", {
    data: { preset: "burmese_default" },
  });
  expect(subtitle.ok()).toBeTruthy();
  const subtitleJson = await subtitle.json();

  const editSubtitle = await api.patch(apiBase + "/subtitles/" + subtitleJson.id, {
    data: { cues: [{ start: 0, end: 2, text: "မြန်မာစာ E2E" }] },
  });
  expect(editSubtitle.ok()).toBeTruthy();

  expect((await api.post(apiBase + "/episodes/" + episodeId + "/subtitles/approve")).ok()).toBeTruthy();
  expect((await api.patch(apiBase + "/episodes/" + episodeId, { data: { status: "needs_approval" } })).ok()).toBeTruthy();

  const approve = await api.post(apiBase + "/episodes/" + episodeId + "/review/approve", {
    data: {
      video_watched: true,
      audio_checked: true,
      subtitle_timing_checked: true,
      thumbnail_present: true,
    },
  });
  expect(approve.ok()).toBeTruthy();

  const exportResponse = await api.post(apiBase + "/episodes/" + episodeId + "/export/mock-drive");
  expect(exportResponse.ok()).toBeTruthy();
  expect((await exportResponse.json()).status).toBe("completed");

  await page.goto("/episodes/" + episodeId + "/export");
  await expect(page.getByText(/Mock Drive/i)).toBeVisible();
});
