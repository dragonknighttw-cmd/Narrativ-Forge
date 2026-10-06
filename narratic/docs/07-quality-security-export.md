# Narrativ Forge — Quality, Security & Export

## Quality gates

### Script
Hook, target duration, scene purpose, cliffhanger/resolution.

### Asset
Scene asset exists, aspect ratio, voice duration, commercial-use status.

### Processing
Successful render, 9:16, audio track, no corrupted output.

### Subtitle
No overlap, no missing text, start < end, 1–7 sec target window, Burmese text, reading-speed warning.

### Review
Complete playback, clear audio, readable subtitle, thumbnail selected, critical issues = 0.

### Export
Status approved, required files complete, metadata valid, Drive connected.

## Drive package

```
/narrativ-forge/YYYY-MM-DD/content-id/
  video.mp4
  subtitles.srt
  subtitles.vtt
  transcript.txt
  script.md
  metadata.json
  thumbnail.jpg
  export-manifest.json
```

Export rules:
- approved content only
- repeated export must be idempotent
- versioned update rather than duplicate folder
- failed/partial upload is retryable
- Drive file IDs stored in DB
- OAuth tokens stay server-side

## Security baseline

- invite-only
- backend RBAC
- server-side OAuth
- no secrets in Git/localStorage
- narrow Drive scope
- MIME/extension validation
- file-size limits
- filename sanitization
- path traversal protection
- CORS allowlist
- auth/upload rate limits
- no secrets in logs
- audit approval/export
- preserve failed jobs
- soft-delete
- backups
- export-manifest checksum

## Reliability baseline

Original, draft, preview, and final are separate versions. Failed jobs remain diagnosable/retryable.
