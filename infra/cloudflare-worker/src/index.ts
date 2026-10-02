interface Env {
  API_ORIGIN: string;
  EDGE_SHARED_SECRET?: string;
}

const HOP_BY_HOP = new Set([
  "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
  "te", "trailer", "transfer-encoding", "upgrade",
]);

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const incoming = new URL(request.url);
    const origin = env.API_ORIGIN.replace(/\/$/, "");
    const target = new URL(origin + incoming.pathname + incoming.search);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: {
        "Access-Control-Allow-Origin": request.headers.get("Origin") ?? "",
        "Access-Control-Allow-Methods": "GET,POST,PATCH,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Max-Age": "600",
      }});
    }

    const headers = new Headers(request.headers);
    for (const name of HOP_BY_HOP) headers.delete(name);

    if (env.EDGE_SHARED_SECRET) headers.set("X-Narrativ-Edge-Secret", env.EDGE_SHARED_SECRET);
    headers.set("X-Narrativ-Edge", "cloudflare-worker");
    headers.set("X-Forwarded-Host", incoming.host);
    headers.set("X-Forwarded-Proto", incoming.protocol.replace(":", ""));

    const upstream = new Request(target.toString(), {
      method: request.method,
      headers,
      body: request.method === "GET" || request.method === "HEAD" ? undefined : request.body,
      redirect: "manual",
    });

    let response: Response;
    try {
      response = await fetch(upstream);
    } catch {
      return new Response(JSON.stringify({ detail: "API upstream unavailable" }), {
        status: 502,
        headers: { "content-type": "application/json", "cache-control": "no-store" },
      });
    }

    const out = new Response(response.body, response);
    out.headers.set("cache-control", "no-store");
    out.headers.set("X-Content-Type-Options", "nosniff");
    out.headers.set("X-Frame-Options", "DENY");
    out.headers.set("Referrer-Policy", "same-origin");
    return out;
  },
};
