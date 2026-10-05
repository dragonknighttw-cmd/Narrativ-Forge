# Secret rotation runbook

## Secrets covered

- SESSION_SECRET
- OAUTH_ENCRYPTION_KEY
- CLOUDINARY_API_SECRET
- B2_APPLICATION_KEY / key ID
- SUPABASE_SERVICE_ROLE_KEY
- CLOUDFLARE_WHISPER_SHARED_SECRET
- Google OAuth client secret
- SMTP password
- Stripe secret/webhook secret
- Sentry DSN when rotation is required

## General procedure

1. Create the replacement credential at the provider.
2. Add/update it in the deployment secret store, never Git.
3. If the credential is shared between two services, update both sides before relying on the new value.
4. Deploy/restart the affected service.
5. Verify configuration through a non-secret health/config check.
6. Revoke the old credential only after the replacement is confirmed.
7. Record the rotation date and affected service in the operational log.

## Cloudflare Whisper shared secret

The same secret must be configured in:

- GitHub Actions secret CLOUDFLARE_WHISPER_SHARED_SECRET
- Render CLOUDFLARE_WHISPER_SHARED_SECRET
- Cloudflare Worker secret NARRATIV_SHARED_SECRET

Do not print the value while verifying.

## OAuth encryption key

Changing OAUTH_ENCRYPTION_KEY invalidates existing encrypted OAuth material unless data is re-encrypted first. Plan a controlled migration before rotating it in production.

## Session secret

Changing SESSION_SECRET invalidates existing signed sessions. Treat this as a controlled logout event.
