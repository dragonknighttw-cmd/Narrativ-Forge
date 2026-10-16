"""Zero-cost Neural Text-to-Speech service using Microsoft Edge Neural TTS.

Provides high-quality synthetic speech without cloud API fees.
Natively supports Burmese (my-MM-NilarNeural, my-MM-ThihaNeural)
and English (en-US-JennyNeural, en-US-GuyNeural, en-US-AriaNeural).
"""

from __future__ import annotations

import asyncio
import io
import logging
import os
from pathlib import Path
from typing import Any, AsyncGenerator

logger = logging.getLogger(__name__)

# Supported voice catalog with zero-cost Edge Neural voices
VOICE_CATALOG = {
    "burmese_female": "my-MM-NilarNeural",
    "burmese_male": "my-MM-ThihaNeural",
    "english_female": "en-US-JennyNeural",
    "english_male": "en-US-GuyNeural",
    "english_aria": "en-US-AriaNeural",
    "english_uk_female": "en-GB-SoniaNeural",
    "english_uk_male": "en-GB-RyanNeural",
}

DEFAULT_VOICE = "my-MM-NilarNeural"


class EdgeTTSService:
    """Async Edge-TTS audio generator and subtitle timing extractor."""

    @classmethod
    def get_supported_voices(cls) -> dict[str, str]:
        """Return human-readable key to Edge-TTS voice identifier."""
        return VOICE_CATALOG

    @classmethod
    def resolve_voice(cls, voice_key_or_name: str | None) -> str:
        """Resolve voice name or alias to canonical Edge Neural voice identifier."""
        if not voice_key_or_name:
            return DEFAULT_VOICE
        # Check alias
        if voice_key_or_name.lower() in VOICE_CATALOG:
            return VOICE_CATALOG[voice_key_or_name.lower()]
        # Direct voice string passed
        return voice_key_or_name

    @classmethod
    async def synthesize_to_file(
        cls,
        text: str,
        output_file_path: str | Path,
        voice: str | None = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> dict[str, Any]:
        """Synthesize text into an MP3 file on disk.

        Returns metadata including path, byte size, and word boundaries.
        """
        import edge_tts

        selected_voice = cls.resolve_voice(voice)
        output_path = Path(output_file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Synthesizing speech via Edge-TTS (voice=%s, target=%s)",
            selected_voice,
            output_path.name,
        )

        communicate = edge_tts.Communicate(
            text=text,
            voice=selected_voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )

        submaker = edge_tts.SubMaker()
        total_bytes = 0

        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                    total_bytes += len(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)

        vtt_content = submaker.get_vtt()

        return {
            "status": "success",
            "voice": selected_voice,
            "file_path": str(output_path),
            "file_size_bytes": total_bytes,
            "vtt_subtitles": vtt_content,
        }

    @classmethod
    async def synthesize_to_bytes(
        cls,
        text: str,
        voice: str | None = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> tuple[bytes, str]:
        """Synthesize text into raw MP3 bytes in memory.

        Returns (audio_bytes, vtt_content).
        """
        import edge_tts

        selected_voice = cls.resolve_voice(voice)
        communicate = edge_tts.Communicate(
            text=text,
            voice=selected_voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )

        submaker = edge_tts.SubMaker()
        audio_buffer = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

        audio_bytes = audio_buffer.getvalue()
        vtt_content = submaker.get_vtt()

        return audio_bytes, vtt_content
