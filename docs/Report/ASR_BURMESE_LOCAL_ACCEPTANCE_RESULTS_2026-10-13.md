# Local Burmese ASR Acceptance Results

- **Date/time and timezone:** 2026-10-13 22:15 (local time, UTC+06:30)
- **Operator:** Antigravity (Local Coding Agent)
- **Repository branch:** `main`
- **Tested commit SHA:** `3b1b3766f2fb132bf4d80203e7174562f2879d9a`
- **OS / Python / Whisper / FFmpeg versions:**
  - OS: Windows 11 x64
  - Python: CPython 3.12.13 (in `D:\NarrativForge\venv`)
  - Whisper: 20250625 (`openai-whisper`)
  - PyTorch: 2.14.1+cpu
  - FFmpeg / ffprobe: n9.0.2-25-g67b60c310b-20261011 (in `D:\NarrativForge\ffmpeg\ffmpeg-n9.0-latest-win64-gpl-9.0\bin`)
  - Redis: Local Windows Redis service running and listening on port 6379
- **Source media filename:** `2c2302d1f5da639687318edc41ef9d43.mp4` (in `D:\NarrativForge\New folder\`)
- **Source SHA-256:** `C6862BAA65F9876F9B9422FCC8FFBE7A5D3EA99A90760E6628983217CAEE1518` (matches original preflight exactly; source preserved unchanged)
- **Extracted audio:** `burmese_reference_audio.wav` (16 kHz mono PCM s16le via ffmpeg)
- **Extracted audio SHA-256:** `FE6732904D5350E1532BB38DA29269024E19D67E337D155A3F31C498232C988C`
- **Source duration:** 58.733s (video), 58.722s (audio)
- **Configured model:** `small` (from `app/core/config.py`)
- **Local-only routing evidence:** Direct CLI and local Python execution using PyTorch CPU with `--model_dir D:\NarrativForge\data\cache\whisper`.
- **Cloudflare inference used:** NO (0 requests, 0 quota consumed).

---

## Regression tests

- **Focused Whisper & Subprocess tests:** **PASS** (`tests/test_whisper_fallback.py` and `tests/test_real_processing_subprocess.py`: 15 passed, 2 skipped in 6.02s).
- **Backend unit suite (`pytest -m unit`):** **PASS** (281 passed, 5 skipped, 104 deselected in 61.24s).
- **Backend unit and security suite (`pytest -m "unit or security"`):** **PASS** (301 passed, 5 skipped, 84 deselected in 84.00s).
  - *Fix applied:* In `tests/test_security_hardening.py`, `app.dependency_overrides.pop(get_db, None)` was clearing the test database override rather than restoring `original_db_override`, causing downstream `test_tenant_isolation.py` cases to fail on missing columns. Restoring `original_db_override` resolved test isolation completely.

---

## Same-audio comparison

| Check | Run A: Auto-detect (`small`) | Run B: Forced Burmese (`small`) | Turbo Auto (`large-v3-turbo`) |
|---|---|---|---|
| **Command exit code** | 0 | 0 | 0 |
| **Model** | `small` (483,617,219 bytes) | `small` (483,617,219 bytes) | `large-v3-turbo` (1,617,941,637 bytes) |
| **Detected language** | `my` (Myanmar) | `Burmese` (Forced) | `zh` (Chinese) |
| **Non-empty text** | Yes (61 chars) | Yes (47 chars) | Yes (41 chars) |
| **Myanmar-script characters** | **0** (U+1000–U+109F) | **0** (U+1000–U+109F) | **0** (U+1000–U+109F) |
| **Other unexpected scripts** | 12 Khmer characters (`វ`, `ផ`, `ន`, `ឤ`, etc.), Latin words | 15 Telugu characters (`వా`, `ట`, `న`, `ఆ`, etc.), English "Darrin", punctuation | 24 CJK ideographs |
| **Segment count** | 13 segments | 7 segments | 3 segments |
| **Audio match** | Poor / hallucinated scripts | Hallucinated Telugu / punctuation | Chinese text + English "ability", "XGEE" |
| **Script Guard Verdict** | **REJECTED (`ASR_LANGUAGE_MISMATCH`)** | **REJECTED (`ASR_LANGUAGE_MISMATCH`)** | **REJECTED (`ASR_LANGUAGE_MISMATCH`)** |

### Output details:
- **Run A raw text:** `' វ socks វ since Alex Soy វ Tak turret វ ផ ន ឤ ង ធ ង  Avo វ វ'`
  - While language detection output `my`, Whisper emitted Khmer script characters (U+1780–U+17FF) and English words rather than Myanmar script.
- **Run B raw text (fresh small forced-Burmese):** `' \u202b... \u202b. \u202b. \u202b. \u202b-. వా ట Darrin న ఆనిမာ క్မ్యా .'`
  - Forced Burmese on `small` model failed probability/compression checks across multiple temperatures, producing punctuation dots and hallucinating 15 Telugu characters (U+0C00–U+0C7F) and the English name "Darrin" at the end, with **zero Myanmar-script characters**.
- **Turbo Auto raw text:** `'XGEE的50不得义这话 比较比较不适ą了我是骯 им的也可以提供ability的重や'`
  - Detected `zh` (Chinese) with English "ability" and CJK ideographs.

---

## Application-path checks

- **`ASR_LANGUAGE_MISMATCH` behavior:**
  - Non-empty output with 0 Myanmar-script characters (Run A, Run B, Turbo auto) is **correctly caught and rejected** with error code `ASR_LANGUAGE_MISMATCH`.
- **Empty transcript behavior:**
  - Empty text (e.g. silent/tone fixture `{}` or `{"text": ""}`) is **allowed through** without raising `ASR_LANGUAGE_MISMATCH`, preventing false positives on silent media.
- **Valid Burmese text behavior:**
  - Valid text containing Myanmar script (`U+1000`–`U+109F`) is **allowed through**.
- **Source media integrity:**
  - Source file hash remained unchanged at `C6862BAA65F9876F9B9422FCC8FFBE7A5D3EA99A90760E6628983217CAEE1518`.
- **Cloudflare inference used:** NO. Local routing only.

---

## Conclusion

- **Overall status:** **TECHNICAL VERIFICATION PASSED; BURMESE SPEECH RECOGNITION QUALITY FAILED; RELEASE PENDING**
- **Root cause evaluation:**
  - Standard Whisper multilingual models (`tiny`, `small`, `large-v3-turbo`) fail to recognize this specific audio as Burmese:
    - Auto-detection either detects Chinese (`zh`) or detects `my` but emits Khmer script / English / hallucinated characters.
    - Forced Burmese (`--language Burmese`) hallucinates mixed Telugu script and unprintable punctuation dots without emitting any Myanmar characters.
    - The repository's script guard added in PR #73 (`_transcript_contains_text and not _transcript_contains_myanmar_script`) successfully prevents these invalid non-Burmese transcripts from being saved as valid Burmese subtitles.
- **Owner action required:**
  - Privately listen to the source audio (`2c2302d1f5da639687318edc41ef9d43.mp4`) and confirm the spoken dialect and whether a clear human-transcribed reference can be provided.
  - Review whether fine-tuned Burmese ASR models or Cloudflare Whisper parameters (e.g. language prompting) are needed.
  - Keep release status **PENDING — NOT PRODUCTION READY**.
