# Storage

> Owner: Storage/platform maintainers  
> Update when: provider routing, lifecycle, retention, or recovery rules change  
> Last Updated: 2026-10-08  
> Do NOT put here: credentials

## Routing

Current application design uses hybrid routing:

| Data | Provider |
|---|---|
| Raw video/audio/large media | Backblaze B2 |
| Small images/thumbnails/previews | Cloudinary |
| SRT/manifests/small workflow files | Supabase Storage |
| Temporary development data | local storage |
| Approved final output | Google Drive |

Routing thresholds and asset-type rules in application code are authoritative over simplified legacy descriptions.

## Lifecycle

Default operational targets:
- local working/temp: short retention;
- B2 raw/intermediate: retention after export/reference checks;
- Cloudinary unused previews: longer cleanup window;
- failed-job artifacts: investigation window;
- approved final output: preserve in Drive;
- required metadata/subtitles: preserve according to product policy.

These are policy defaults, not permission for blind deletion.

## Safety

Before deletion:
1. Verify workflow references.
2. Protect original source assets.
3. Protect approved/final/only-copy assets.
4. Record cleanup/audit state.
5. Preserve recovery paths where required.

Thresholds:
- 80% warning.
- 90% high warning.
- 95% emergency cleanup/block non-essential temporary work.

## Verification

Real B2, Supabase, Cloudinary lifecycle, cleanup, archive/cold storage, deletion/PII purge, and backup/restore remain VERIFY until real evidence exists.
