# Security and Risks

**Generated:** 2026-10-12  
**Inspected repository checkpoint:** `main`, HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4`

## Findings and risk register

| Severity / status | Finding | Evidence and limitation |
|---|---|---|
| High product-quality risk — open | Historical worker behavior asserted `language: my`; current `tiny` transcript contains CJK ideographs and no Myanmar-script characters. The uncommitted fix now preserves detected/provider language. | [`real_processing.py`](../../web-platform/backend/app/services/real_processing.py), [sample report](BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md); not a security vulnerability, but no candidate may be approved as Burmese without review. |
| Resolved test reliability issue | [`test_real_processing_subprocess.py`](../../web-platform/backend/tests/test_real_processing_subprocess.py) had a 0.2-second process-tree startup window that could expire before Windows child startup completed. The test-only window is now 2 seconds; the focused file passes 6/2. | [Test results](01_TEST_RESULTS.md). Production timeout behavior was not changed. |
| Not verified | No fresh security review of all application code was performed for this report. | Do not interpret this report as a security audit or a clean bill of health. |
| Not verified | Production managed database restore, continuous worker operations, and current cloud settings were not revalidated. | See [cloud status](04_CLOUD_DEPLOYMENT_STATUS.md). |

## Existing controls documented by the project

[`SECURITY.md`](../../SECURITY.md) documents server-side authentication and tenant authorization, protected secrets, upload validation, webhook protections, audit scoping, and human approval before final export/publication. Repository docs record historical Security and CodeQL workflow passes on exact earlier SHAs; they are not fresh scans on the inspected worktree.

The backend includes tenant-isolation coverage in [`test_tenant_isolation.py`](../../web-platform/backend/tests/test_tenant_isolation.py), but that suite was not run during this report task. Authentication/tenant-isolation acceptance on the current deployment is **NOT VERIFIED**.

## Secret and data handling

- No `.env` or credential values were read or included in this report.
- The supplied media, transcript text, database, and raw logs were not copied into Git or `docs/Report/`.
- Local machine paths in the older Windows report have been replaced by a placeholder.
- The sample's transcript should remain a draft/unaccepted output until its spoken language and content are reviewed by an authorized Burmese speaker.

## Recovery and data-loss risks

The local SQLite/asset evidence is synthetic/local-only. It is not a managed production backup/restore drill. Preserve originals and avoid deleting local episode assets independently of their database references. Production recovery remains owner-approved and unverified.
