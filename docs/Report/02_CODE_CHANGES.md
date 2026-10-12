# Code Changes

**Generated:** 2026-10-12  
**Inspected repository checkpoint:** `main`, HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4`  
**Worktree:** Changes are uncommitted; no commit or push was requested or made.

## Implementation change

| File | Change | Root cause / validation |
|---|---|---|
| [`real_processing.py`](../../web-platform/backend/app/services/real_processing.py) | Subprocess text capture now explicitly uses UTF-8 and `errors="backslashreplace"`. | Windows' default code page could not decode Burmese/non-ASCII child-process output, raising `UnicodeDecodeError` during transcript processing. |
| [`real_processing.py`](../../web-platform/backend/app/services/real_processing.py) | Local Whisper no longer receives a forced `--language my`; backend no longer overwrites provider language metadata or invents a Burmese language label. | The supplied sample showed that forced language metadata can conceal language-recognition failure. Whisper fallback tests verify auto-detection is requested and missing cloud language metadata stays missing. |
| [`test_real_processing_subprocess.py`](../../web-platform/backend/tests/test_real_processing_subprocess.py) | Added a regression case for Burmese UTF-8 output plus malformed bytes; increased a Windows process-tree timeout test's startup window from 0.2 to 2 seconds. | Validates text survives and invalid bytes are escaped rather than crashing the wrapper. The previous timeout raced before child startup under Windows scheduling; the final focused test file passed 6/2. No production timeout behavior changed. |

## Documentation changes

- [`BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md`](BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md): records the forced-language/CJK mismatch and unusable small-model auto/forced-language results.
- [`BURMESE_MEDIA_ACCEPTANCE.md`](../BURMESE_MEDIA_ACCEPTANCE.md): keeps acceptance pending and warns against approving the current transcript.
- [`CURRENT_STATE.md`](../../CURRENT_STATE.md): updates the sample evidence and outstanding review gates.
- [`LOCAL_WINDOWS_UNICODE_RUNTIME_REPORT.md`](LOCAL_WINDOWS_UNICODE_RUNTIME_REPORT.md): records the subprocess fix, test instability, and historical Windows restore-test resolution; machine-specific absolute paths were redacted.
- This package: [`00_EXECUTIVE_SUMMARY.md`](00_EXECUTIVE_SUMMARY.md) through [`07_EVIDENCE_INDEX.md`](07_EVIDENCE_INDEX.md).

## Limitations

- No transcript was edited or represented as correct. The language-detection correction lets Whisper detect language; it does not guarantee Burmese recognition.
- The language-detection correction is uncommitted and has test coverage, but has not yet been exercised by a fresh canonical worker run.
- The local worker evidence does not have an exact source SHA in the original runtime record.
- No production configuration, cloud inference, secrets, or media files were changed or added to Git.
- All listed changes remain uncommitted.
