# Remaining Work and Owner Actions

**Generated:** 2026-10-12  
**Inspected repository checkpoint:** `main`, HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4`

## Prioritized actions

1. **Confirm the sample language.** Privately listen to the original sample and confirm whether it contains Burmese. If it does, provide a reference transcript or arrange a Burmese-speaking reviewer. Do not paste private speech or credentials into a public issue or report.
2. **Resolve the source-language/ASR mismatch.** `tiny` auto-detection and checksum-verified `large-v3-turbo` auto-detection both report Chinese; the turbo output has 0 Myanmar-script characters. `small` auto-detection reports `my` but has 0 Myanmar-script characters, and forced-`my` `small` produced only 6 characters. Privately confirm the sample's spoken language; if it is Burmese, provide an owner-approved reference or arrange Burmese-speaker review and investigate against the audio. Do not publish current candidates as Burmese.
3. **Verify processing evidence.** Repeat the canonical local worker run with the exact source SHA recorded, verify transcript/output retrieval, subtitle timing, playback, and unchanged input.
4. **Verify exact-SHA CI.** After these local edits are committed by the owner, confirm the applicable workflows on that exact SHA; local test success alone is not merge or production evidence.
5. **Refresh CI status.** Authenticate `gh` locally through its supported interactive flow if the owner wants current workflow results; never put a token in a report or chat. Compare current `main` SHA with each run SHA.
6. **Complete production gates.** Resolve authenticated Whisper 403/preflight path, obtain owner approval for any quota-consuming inference and billable continuous worker, and complete managed restore, storage, OAuth/Drive, SMTP, Stripe, Sentry, performance, accessibility, privacy/legal, and external security reviews.

## Agent-safe next work

- Continue documenting local evidence and run focused tests without secrets or cloud writes.
- Continue inspecting completed local transcript candidates against an owner-approved reference; do not silently relabel or hand-edit ASR text as model output.
- Repeat the canonical worker with auto-detection after the updated code is committed, recording the exact SHA and checking the saved language value.

## Owner approval / access required

- Confirmation of the sample's spoken language and whether it may be processed; if it is Burmese, a reference transcript or human language review.
- Protected provider configuration and explicit approval before authenticated/possibly quota-consuming inference.
- Approval before provisioning paid persistent worker capacity or making production deployment/configuration changes.
- Authorized access for fresh GitHub Actions/cloud status checks if `gh` authentication is required.
- Legal/privacy and external security acceptance.

Never send secret values in chat, reports, source, logs, or issue comments.
