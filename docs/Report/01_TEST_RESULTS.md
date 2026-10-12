# Test Results

**Generated:** 2026-10-12  
**Inspected repository checkpoint:** `main`, HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4`  
**Worktree:** Dirty during local test execution. Each local result below is against that base HEAD plus the uncommitted working tree; no commit represents the tested tree.

Statuses: PASS = executed and passed; FAIL = executed and failed; BLOCKED = prevented by environment/approval; NOT RUN = not attempted; NOT VERIFIED = evidence is incomplete or not freshly confirmed.

## Local checks

| Test / command | Status | Tested commit / tree | Result and evidence |
|---|---|---|---|
| `python -m pytest tests\test_real_processing_subprocess.py -q` from `web-platform\backend` | **PASS** | Base `95aa9163cc40383a8c44c3a5f445e4de899116e4` + final dirty worktree | Final run: `6 passed, 2 skipped in 4.41s`. The test-only process-start window was increased from 0.2 to 2 seconds; production timeout behavior was unchanged. |
| `python -m pytest tests\test_whisper_fallback.py tests\test_real_processing_subprocess.py -q` | **PASS** | Base `95aa9163cc40383a8c44c3a5f445e4de899116e4` + dirty worktree | Final rerun from `web-platform\backend`: `9 passed, 2 skipped in 6.49s`; covers local auto-detection arguments and does not fabricate provider language metadata. |
| `python -m pytest tests\test_whisper_fallback.py tests\test_foundation.py -q` | **PASS** | Same base HEAD + dirty worktree | `38 passed, 1 skipped in 39.66s`. |
| Earlier run of the same focused file | **FAIL (race reproduced)** | Same base HEAD + earlier dirty worktree before timeout-test adjustment | Two full-file runs reported `5 passed, 1 failed, 2 skipped`; the process-tree test did not observe the child PID file within 0.2 seconds. Its isolated rerun passed (`1 passed in 61.41s`). |
| `git diff --check` | **PASS** | Final local worktree at base HEAD above | No whitespace errors. |
| Local Windows worker sample processing | **NOT VERIFIED (historical run reported successful)** | Exact tested source SHA **not recorded** | The runtime report records `SAMPLE_WORKER_OK`, completed job, and output/transcript artifacts. The transcript has since been inspected and fails the Burmese-script check. See [sample report](BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md). |
| Whisper `tiny`, forced `--language my` transcript review | **FAIL** | Exact worker source SHA **not recorded** | Transcript metadata is forced to `my`; text has 252 CJK ideographs and zero Myanmar-script characters. It is not acceptable as Burmese output. |
| Whisper `tiny` automatic language detection | **FAIL for Burmese identification** | No repository code SHA applies; local model test | Console reported Chinese. No claim of human-confirmed source language is made. |
| Whisper `small` automatic detection | **FAIL for Burmese transcript quality** | No repository code SHA applies; local model test | Completed: detected `my`, 5 segments, 152 text characters, 0 Myanmar-script characters. Candidate text excluded from repository. |
| Whisper `small` forced to `my` | **FAIL** | No repository code SHA applies; local model test | Candidate outside the repository: 4 segments, 6 text characters, 0 Myanmar-script characters. Not a usable Burmese transcript. |
| Whisper `large-v3-turbo` automatic detection (CPU, local sample) | **FAIL (transcript quality; inference completed)** | No repository code SHA applies; local model test | After resuming the interrupted download, model integrity passed: 1,617,941,637 bytes with SHA-256 `aff26ae408abcba5fbf8813c21e62b0941638c5f6eebfb145be0c9839262a19a`. Whisper completed on the 58.7-second sample, detected `zh` (Chinese), and returned 3 segments / 41 non-whitespace characters: 0 Myanmar-script, 24 CJK ideographs; NFC check passed. Candidate JSON is stored outside the repository; text is not copied into reports. This is a failed Burmese-output attempt, not confirmation of the spoken language. |
| Burmese-speaker/reference transcript review | **NOT RUN** | N/A | No reference transcript or human review evidence is available. |

## Documented CI evidence (not freshly queried)

`gh run list` could not authenticate in this environment. The following PASS results are quoted from repository documentation and apply only to the exact SHA shown, not to inspected local HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4`.

| Workflow | Status | Exact workflow SHA | Evidence |
|---|---|---|---|
| CI | PASS (documented) | `b374df9e1e455e35eaa9847d78fb7c9af70f2393` | [Run #38201576482](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576482) |
| Security | PASS (documented) | `b374df9e1e455e35eaa9847d78fb7c9af70f2393` | [Run #38201576514](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576514) |
| CodeQL | PASS (documented) | `b374df9e1e455e35eaa9847d78fb7c9af70f2393` | [Run #38201576494](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576494) |
| Repository Gate | PASS (documented) | `b374df9e1e455e35eaa9847d78fb7c9af70f2393` | [Run #38201576503](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576503) |
| Real Worker Evidence (ephemeral) | PASS (documented) | `b374df9e1e455e35eaa9847d78fb7c9af70f2393` | [Run #38201576538](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576538); synthetic/ephemeral, not a persistent production worker |
| Windows Local Runtime Evidence | PASS (documented) | `b374df9e1e455e35eaa9847d78fb7c9af70f2393` | [Run #38201576459](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576459) |
| Windows Portable Package Evidence | PASS (documented) | `b374df9e1e455e35eaa9847d78fb7c9af70f2393` | [Run #38201576528](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576528) |
| Local Runtime Evidence | PASS (documented) | `b374df9e1e455e35eaa9847d78fb7c9af70f2393` | [Run #38201576477](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576477) |

These historical workflows do not establish production deployment, authenticated Burmese transcription quality, managed recovery, or a continuously running worker.
