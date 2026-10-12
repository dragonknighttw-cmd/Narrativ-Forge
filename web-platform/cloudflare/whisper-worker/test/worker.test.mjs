import assert from "node:assert/strict";
import test from "node:test";
import worker from "../src/index.ts";

const secret = "test-only-secret-value-with-at-least-32-characters";

function base64url(bytes) {
  return Buffer.from(bytes).toString("base64url");
}

async function signedToken(payload) {
  const encoded = base64url(Buffer.from(JSON.stringify(payload), "utf8"));
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(encoded));
  return encoded + "." + base64url(signature);
}

function env(aiRun) {
  return {
    NARRATIV_SHARED_SECRET: secret,
    ALLOWED_ORIGIN: "https://harmonious-nasturtium-53a1d6.netlify.app",
    AI: { run: aiRun },
  };
}

test("provider diagnostics are not returned to callers on inference failure", async () => {
  const token = await signedToken({
    sub: "test-user",
    episode_id: "episode-test",
    exp: Math.floor(Date.now() / 1000) + 60,
    max_audio_seconds: 1,
  });
  const sensitiveDiagnostic = "upstream request failed with internal-token-should-not-leak";
  const request = new Request("https://worker.test/", {
    method: "POST",
    headers: {
      Authorization: "Bearer " + token,
      "Content-Type": "audio/wav",
      "X-Narrativ-Episode": "episode-test",
      Origin: "https://harmonious-nasturtium-53a1d6.netlify.app",
    },
    body: new Uint8Array(44),
  });

  const response = await worker.fetch(request, env(async () => {
    throw new Error(sensitiveDiagnostic);
  }));
  const body = await response.text();

  assert.equal(response.status, 502);
  assert.deepEqual(JSON.parse(body), { error: "Whisper inference failed" });
  assert.equal(body.includes(sensitiveDiagnostic), false);
  assert.equal(body.includes("internal-token-should-not-leak"), false);
});

test("invalid processing tokens are rejected before inference", async () => {
  let inferenceCalled = false;
  const request = new Request("https://worker.test/", {
    method: "POST",
    headers: {
      Authorization: "Bearer invalid",
      "Content-Type": "audio/wav",
      "X-Narrativ-Episode": "episode-test",
      Origin: "https://harmonious-nasturtium-53a1d6.netlify.app",
    },
    body: new Uint8Array(44),
  });
  const response = await worker.fetch(request, env(async () => {
    inferenceCalled = true;
    return { text: "unexpected" };
  }));

  assert.equal(response.status, 401);
  assert.equal(inferenceCalled, false);
});
