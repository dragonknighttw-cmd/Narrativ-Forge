"""Zero-cost Storyboard Generation Service using Pollinations.ai FLUX.

Generates high-resolution vertical (9:16 - 720x1280) and widescreen (16:9 - 1280x720)
cinematic scene visuals for episodic video production, TikTok, and YouTube Shorts.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any
import urllib.parse
import httpx

logger = logging.getLogger(__name__)

POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"


class StoryboardGeneratorService:
    """Async FLUX image generation service for scene storyboards."""

    @classmethod
    def build_storyboard_url(
        cls,
        prompt: str,
        *,
        aspect_ratio: str = "9:16",
        model: str = "flux",
        seed: int | None = None,
        enhance: bool = True,
        negative_prompt: str | None = None,
    ) -> str:
        """Construct a high-performance direct CDN URL for a scene visual.

        Supported aspect ratios:
        - '9:16': 720x1280 (vertical story, TikTok, Reels, YouTube Shorts)
        - '16:9': 1280x720 (cinematic widescreen)
        - '1:1': 1024x1024 (square)
        """
        # Optimize cinematic prompt
        cinematic_enhancer = (
            "cinematic still, 8k resolution, photorealistic, dramatic lighting, masterpiece"
        )
        final_prompt = f"{prompt}, {cinematic_enhancer}" if enhance else prompt
        encoded_prompt = urllib.parse.quote(final_prompt)

        # Dimension calculation
        if aspect_ratio == "9:16":
            width, height = 720, 1280
        elif aspect_ratio == "16:9":
            width, height = 1280, 720
        else:
            width, height = 1024, 1024

        query_params = [
            f"width={width}",
            f"height={height}",
            f"model={model}",
            "nologo=true",
        ]

        if seed is not None:
            query_params.append(f"seed={seed}")
        if negative_prompt:
            query_params.append(f"negative={urllib.parse.quote(negative_prompt)}")

        return f"{POLLINATIONS_BASE_URL}/{encoded_prompt}?{'&'.join(query_params)}"

    @classmethod
    async def generate_and_save_scene(
        cls,
        prompt: str,
        output_file_path: str | Path,
        *,
        aspect_ratio: str = "9:16",
        model: str = "flux",
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Fetch image bytes directly from FLUX and save as JPG/PNG file."""
        url = cls.build_storyboard_url(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            model=model,
            seed=seed,
        )
        output_path = Path(output_file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Fetching FLUX storyboard (aspect=%s, target=%s)",
            aspect_ratio,
            output_path.name,
        )

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Pollinations FLUX generation failed with status {response.status_code}"
                )
            output_path.write_bytes(response.content)

        return {
            "status": "success",
            "file_path": str(output_path),
            "file_size_bytes": len(response.content),
            "image_url": url,
            "aspect_ratio": aspect_ratio,
        }
