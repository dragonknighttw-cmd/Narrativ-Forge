# Narrativ Forge Cloudflare Edge Worker

This Worker is the lightweight edge proxy in front of the Render API.

## Production

Set API_ORIGIN to the public Render API origin. If an additional shared edge secret is desired, set it as a Worker secret:

npx wrangler secret put EDGE_SHARED_SECRET

Do not put credentials in wrangler.toml.

The Worker does not process media, run FFmpeg/Whisper, or replace B2. Render remains the API/processing runtime and Backblaze B2 remains the media store.

Cloudflare WAF/rate limiting should be configured at the zone/edge layer rather than implemented as an in-memory Worker counter.
