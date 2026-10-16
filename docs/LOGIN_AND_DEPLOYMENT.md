# Narrativ Forge login and Render deployment checklist

## Where to sign in

Open the frontend login page:

- https://narrativ-forge-frontend.onrender.com/login

Use the email and password belonging to the invited Supabase Auth account. The application exchanges the Supabase access token with the backend and then sets an HTTP-only application session cookie. Do not share passwords or service-role keys in chat, issues, logs, or repository files.

## Important current-state note

The Render services were last inspected on 2026-10-16. Their dashboard settings still use the old `web-platform/backend` and `web-platform/frontend` paths, while the current repository paths are under `apps/web-platform/`. The services have auto-deploy disabled, and the deployed commits lag behind `main`. Therefore, the URL is the intended login location, but successful production login has not been verified.

This document and the Render blueprint changes do not deploy or modify live services. Treat production login as unverified until the corrected configuration is tested in a preview/staging deployment.

## Canonical Supabase project

The production project was explicitly confirmed on 2026-10-16:

- Project name: `Narrativ-Forge`
- Project ref: `xrhlefglqwquhvpoevsg`
- Project URL: `https://xrhlefglqwquhvpoevsg.supabase.co`

The API `SUPABASE_URL` and frontend `NEXT_PUBLIC_SUPABASE_URL` must both refer to this project. The public anon/publishable key must be obtained from this same project. Do not copy a key from `Narrativ-Forge-1`. The project selection is documented here only; no live Render variables have been changed.

## Required Render configuration

The blueprint declares these values as `sync: false`; set them in the Render dashboard for the matching service, without committing secrets:

### API service

- `APP_ENV=production`
- `DATABASE_URL` — the confirmed canonical production database only
- `SESSION_SECRET` — strong random secret, at least 32 characters
- `SESSION_COOKIE_SECURE=true`
- `OAUTH_ENCRYPTION_KEY` — valid Fernet key
- `CORS_ORIGINS=https://narrativ-forge-frontend.onrender.com`
- `TRUSTED_HOSTS=narrativ-forge.onrender.com`
- `FRONTEND_BASE_URL=https://narrativ-forge-frontend.onrender.com`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` — secret; never expose to the browser
- `SUPABASE_OWNER_USER_ID` and `SUPABASE_OWNER_EMAIL` — match the intended confirmed Supabase Auth owner identity
- Required storage provider credentials for the configured `STORAGE_PROVIDER`

### Frontend service

- `NEXT_PUBLIC_API_BASE_URL=https://narrativ-forge.onrender.com/api/v1`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

Only the Supabase URL and anon/publishable key belong in frontend build variables. Never put the Supabase service-role key in a `NEXT_PUBLIC_*` variable.

## Safe release sequence

1. Review and merge the code/configuration PRs only after required checks pass.
2. Confirm which Supabase project is canonical and confirm the Render database URL points to it; do not run migrations against an unconfirmed project.
3. Compare the existing Render services with `render.yaml` before syncing the blueprint. Confirm the service names match so syncing does not accidentally create duplicate services.
4. Set and verify required environment variables without exposing secret values.
5. Deploy to a preview/staging target first and verify `/api/v1/health`, Supabase login, first-owner provisioning, cookie persistence, and dashboard access.
6. Deploy production only after explicit approval and a tested rollback/backup plan.

## Login troubleshooting

- If the page is unavailable, check the frontend Render service status and build logs.
- If sign-in reports a generic failure, check frontend `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`, API `SUPABASE_URL` and `SUPABASE_ANON_KEY`, API availability, CORS origin, and the configured owner UUID/email.
- The first Owner is provisioned only when the confirmed Supabase Auth UUID and email match the server-side configuration and the configured organization exists.
- Never disable email confirmation or weaken the owner UUID/email check to work around a login issue.

## Database access hardening

The backend is the only application data access path; the browser uses Supabase Auth for identity and sends its access token to the API. Do not grant browser roles direct table access as a workaround for login problems.

The read-only production audit on 2026-10-16 found RLS enabled on 41 public tables with no policies, plus broad table grants for the Supabase `anon` and `authenticated` roles on five tables. RLS with no policies is default-deny, but the extra grants are unnecessary. Revision `0021_revoke_client_grants` revokes table and sequence privileges from those client roles on PostgreSQL/Supabase while preserving server-side database access. It has not been applied to production.

Supabase Security Advisor also reports leaked-password protection disabled. Enable it through the Supabase Auth password security settings after reviewing the expected sign-up/password-reset behavior; this is a project setting and is not changed by repository migrations. After any approved staging migration, verify the advisor and confirm client roles have no table/sequence privileges. Do not add permissive RLS policies merely to silence the advisor.
