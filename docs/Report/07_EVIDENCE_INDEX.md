# Evidence Index

**Generated:** 2026-10-12  
**Inspected repository checkpoint:** `main`, HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4`  
**Evidence handling:** Raw media, transcript text, database files, and unrestricted local logs are not included here.

## Repository evidence

| Evidence | Location / reference | Scope |
|---|---|---|
| Current code/worktree state | HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4`; dirty worktree | This report package and local test changes have not been committed. |
| Windows runtime history | [Windows runtime report](LOCAL_WINDOWS_UNICODE_RUNTIME_REPORT.md) | Historical local synthetic worker, dependencies, artifacts, and subprocess fix. Exact worker source SHA was not recorded. Local absolute paths were sanitized. |
| Burmese sample findings | [Sample preflight report](BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md) | Technical media facts, local worker outcome, and failed `tiny` transcript script check. Media/transcript content excluded. |
| Higher-capacity Whisper attempt | [Test results](01_TEST_RESULTS.md) | Official `large-v3-turbo` model passed SHA-256 verification; local CPU inference completed, detected Chinese, and produced no Myanmar-script characters. Candidate text is excluded. |
| Acceptance status | [Burmese media checklist](../BURMESE_MEDIA_ACCEPTANCE.md) | Speech-quality review remains pending. |
| Security controls | [`SECURITY.md`](../../SECURITY.md) | Repository security policy and outstanding release gates. |
| Release gates and cloud records | [`CURRENT_STATE.md`](../../CURRENT_STATE.md), [`MASTER_REMAINING_WORK.md`](../MASTER_REMAINING_WORK.md), [`DEPLOYMENT.md`](../DEPLOYMENT.md) | Historical documented status; not freshly queried during this task. |
| Windows diagnostic script | `Check-NarrativForge-Local.ps1` in the external handoff folder | Read-only inventory script; not part of repository. Owner-local absolute path omitted. |

## Local test evidence

- Final full focused subprocess file: base HEAD above plus final dirty worktree; `6 passed, 2 skipped in 4.41s`.
- Earlier full-file runs exposed a process-tree test race at 0.2 seconds; the isolated test passed and the test-only startup window was increased to 2 seconds before the final passing run.
- The CLI test output was obtained directly from pytest. No raw logs were copied to this folder.
- The exact SHA for the earlier canonical Windows worker sample run is unavailable in the source record; see the limitation in the Windows runtime report.
- GitHub CLI could not authenticate, so current run metadata could not be retrieved. Historical workflow URLs and exact SHAs are in [test results](01_TEST_RESULTS.md) and [cloud status](04_CLOUD_DEPLOYMENT_STATUS.md).

## Historical workflow links

See [01_TEST_RESULTS.md](01_TEST_RESULTS.md) for exact-SHA workflow results and [04_CLOUD_DEPLOYMENT_STATUS.md](04_CLOUD_DEPLOYMENT_STATUS.md) for dated Render, Netlify, and Cloudflare observations. Workflow passes are not production acceptance.

## Missing or inaccessible evidence

- Fresh workflow status for local HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4`.
- Exact source commit used by the historical local worker run.
- Usable Burmese Whisper candidate and Burmese-speaker/reference review; `small` auto-detect output had no Myanmar-script characters.
- Burmese-speaker/reference review and confirmation of the sample's spoken language.
- Fresh current cloud settings and health checks.
- Managed production backup/restore and persistent worker evidence.
