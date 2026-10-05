# Narrativ Forge Cloudflare Whisper Worker

Browser extracts audio with ffmpeg.wasm, then this Worker sends it to Cloudflare Workers AI Whisper.

Required configuration:
- Workers AI binding: AI
- Secret: NARRATIV_SHARED_SECRET
- Variable: ALLOWED_ORIGIN

The secret must match backend CLOUDFLARE_WHISPER_SHARED_SECRET. It is never sent to the browser.

Deploy:

    cd web-platform/cloudflare/whisper-worker
    npm install -D wrangler typescript
    npx wrangler secret put NARRATIV_SHARED_SECRET
    npx wrangler deploy

Then set the deployed workers.dev URL as CLOUDFLARE_WHISPER_WORKER_URL in Render.

Workers AI currently has a 10,000-neuron/day free allocation. Whisper is available as @cf/openai/whisper. This is a quota, not unlimited free inference.
