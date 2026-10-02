import json
import re
from pathlib import Path

MYANMAR_RE = re.compile(r"[\u1000-\u109F]")
PRESETS = {
    "burmese_default": {"max_chars": 42, "min_seconds": 1.0, "max_seconds": 7.0, "max_lines": 2},
    "burmese_compact": {"max_chars": 32, "min_seconds": 1.0, "max_seconds": 5.0, "max_lines": 2},
}

def preset_config(name: str):
    return PRESETS.get(name, PRESETS["burmese_default"])

def format_srt_time(seconds: float) -> str:
    total_ms = max(0, round(seconds * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def format_vtt_time(seconds: float) -> str:
    total_ms = max(0, round(seconds * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

def render_srt(cues):
    return "\n\n".join(
        f"{i}\n{format_srt_time(cue['start'])} --> {format_srt_time(cue['end'])}\n{cue['text']}"
        for i, cue in enumerate(cues, 1)
    ) + ("\n" if cues else "")

def render_vtt(cues):
    body = "\n\n".join(
        f"{format_vtt_time(cue['start'])} --> {format_vtt_time(cue['end'])}\n{cue['text']}"
        for cue in cues
    )
    return "WEBVTT\n\n" + body + ("\n" if body else "")

def validate_cues(cues, preset="burmese_default"):
    config = preset_config(preset)
    errors = []
    for index, cue in enumerate(cues, 1):
        start = cue.get("start")
        end = cue.get("end")
        text = str(cue.get("text") or "").strip()
        if not text:
            errors.append({"code": "MISSING_TEXT", "cue": index, "message": "Cue text is empty."})
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            errors.append({"code": "INVALID_TIME", "cue": index, "message": "Cue timing must be numeric."})
            continue
        if start < 0 or end <= start:
            errors.append({"code": "INVALID_TIME", "cue": index, "message": "Cue end must be after start."})
        duration = end - start
        if duration < config["min_seconds"] or duration > config["max_seconds"]:
            errors.append({"code": "DISPLAY_TIME", "cue": index, "message": f"Display time must be {config['min_seconds']:.0f}–{config['max_seconds']:.0f} seconds."})
        if len(text) > config["max_chars"]:
            errors.append({"code": "LINE_LENGTH", "cue": index, "message": f"Text exceeds {config['max_chars']} characters for {preset}."})
        if text and not MYANMAR_RE.search(text):
            errors.append({"code": "BURMESE_TEXT_REQUIRED", "cue": index, "message": "Cue must contain Burmese text."})
        if text.count("\n") + 1 > config["max_lines"]:
            errors.append({"code": "LINE_COUNT", "cue": index, "message": f"Cue must use at most {config['max_lines']} lines."})
        if index > 1:
            previous = cues[index - 2]
            if isinstance(previous.get("end"), (int, float)) and isinstance(start, (int, float)) and start < previous["end"]:
                errors.append({"code": "CUE_OVERLAP", "cue": index, "message": "Cue overlaps the previous cue."})
    return errors

def load_transcript(path: str):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    segments = data.get("segments", [])
    return [
        {"id": index, "start": float(segment["start"]), "end": float(segment["end"]), "text": str(segment.get("text", "")).strip()}
        for index, segment in enumerate(segments, 1)
        if "start" in segment and "end" in segment
    ]
