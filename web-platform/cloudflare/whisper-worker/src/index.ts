interface Env {
  AI: Ai;
  NARRATIV_SHARED_SECRET: string;
  ALLOWED_ORIGIN: string;
}

type TokenPayload = { sub: string; episode_id: string; exp: number };

function base64url(input: ArrayBuffer | Uint8Array): string {
  const bytes = input instanceof Uint8Array ? input : new Uint8Array(input);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}
function fromBase64url(value: string): Uint8Array {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - (value.length % 4)) % 4);
  const binary = atob(normalized);
  return Uint8Array.from(binary, char => char.charCodeAt(0));
}
async function hmac(secret: string, value: string): Promise<ArrayBuffer> {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
  return crypto.subtle.sign("HMAC", key, new TextEncoder().encode(value));
}
async function verifyToken(token: string, secret: string): Promise<TokenPayload | null> {
  const parts = token.split(".");
  if (parts.length !== 2) return null;
  try {
    const expected = await hmac(secret, parts[0]);
    const supplied = fromBase64url(parts[1]);
    if (supplied.length !== new Uint8Array(expected).length) return null;
    const expectedBytes = new Uint8Array(expected);\n    let difference = supplied.length ^ expectedBytes.length;\n    for (let i = 0; i < Math.min(supplied.length, expectedBytes.length); i++) difference |= supplied[i] ^ expectedBytes[i];\n    if (difference !== 0) return null;
    const payload = JSON.parse(new TextDecoder().decode(fromBase64url(parts[0]))) as TokenPayload;
    return payload.exp > Math.floor(Date.now() / 1000) && payload.sub && payload.episode_id ? payload : null;
  } catch { return null; }
}
function corsHeaders(origin: string, allowedOrigin: string): HeadersInit {
  return {
    "Access-Control-Allow-Origin": origin === allowedOrigin ? origin : allowedOrigin,
    "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Narrativ-Episode",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
  };
}
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = request.headers.get("Origin") ?? "";
    const headers = corsHeaders(origin, env.ALLOWED_ORIGIN);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers });
    if (request.method !== "POST") return Response.json({ error: "Method not allowed" }, { status: 405, headers });

    const auth = request.headers.get("Authorization") ?? "";
    const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
    const claims = await verifyToken(token, env.NARRATIV_SHARED_SECRET);
    if (!claims) return Response.json({ error: "Invalid or expired processing token" }, { status: 401, headers });

    const episodeId = request.headers.get("X-Narrativ-Episode") ?? "";
    if (episodeId !== claims.episode_id) return Response.json({ error: "Episode token mismatch" }, { status: 403, headers });

    const contentType = request.headers.get("Content-Type") ?? "audio/wav";
    if (!contentType.startsWith("audio/")) return Response.json({ error: "Audio content is required" }, { status: 415, headers });

    const body = await request.arrayBuffer();
    if (body.byteLength === 0) return Response.json({ error: "Empty audio payload" }, { status: 400, headers });
    if (body.byteLength > 50 * 1024 * 1024) return Response.json({ error: "Audio payload exceeds 50 MB" }, { status: 413, headers });

    try {
      const result = await env.AI.run("@cf/openai/whisper", { audio: body });
      return Response.json({
        provider: "cloudflare_workers_ai",
        model: "@cf/openai/whisper",
        episode_id: claims.episode_id,
        text: result.text ?? "",
        word_count: result.word_count ?? 0,
        vtt: result.vtt ?? "",
      }, { headers });
    } catch (error) {
      return Response.json({ error: "Whisper inference failed", detail: error instanceof Error ? error.message : "Unknown inference error" }, { status: 502, headers });
    }
  },
};