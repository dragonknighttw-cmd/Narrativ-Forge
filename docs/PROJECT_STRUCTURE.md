# Project Structure

This document describes the current active layout. It replaces the former point-in-time file inventory; generated local files and `archive/legacy/` are intentionally excluded.

```text
Narrativ-Forge/
├── apps/
│   ├── mobile/                         # Reserved mobile surface; no shipped mobile runtime is implied
│   └── web-platform/
│       ├── frontend/                   # Next.js / TypeScript web application
│       ├── backend/                    # Backend application source and supporting assets
│       ├── cloudflare/                 # Edge/Cloudflare integration and worker assets
│       └── docs/                       # Web-platform-specific architecture notes
├── docs/                               # Current project, API, deployment and acceptance docs
├── infra/                              # Infrastructure assets and runbooks
├── scripts/                            # Maintenance, backup and verification tooling
├── .github/workflows/                  # CI, security and deployment automation
└── archive/legacy/                     # Historical material; not active runtime code
```

## Placement rules

- Keep browser code in `apps/web-platform/frontend/` and backend code in `apps/web-platform/backend/`.
- Keep Cloudflare-specific deployable assets in `apps/web-platform/cloudflare/`; do not mix them into the browser build.
- `apps/mobile/` is a reserved location only. Add a real mobile implementation there when that product surface is started.
- Root Markdown files describe project-wide policy and status. Put detailed current guides in `docs/`, and do not use archived documentation as an implementation source.

Use `../CURRENT_STATE.md` and `../ROADMAP.md` for current status and planned work.
