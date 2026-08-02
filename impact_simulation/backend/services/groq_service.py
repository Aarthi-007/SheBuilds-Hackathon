"""
Wraps the Groq vision API.

Per context.md: Groq handles universal multimodal perception only — it
converts raw image/video into structured text. No other agent or service
touches raw media directly; everything downstream works off the text
description this service produces.
"""

from __future__ import annotations

import asyncio
import json
import re

from groq import Groq

from backend.config.settings import get_settings

PERCEPTION_INSTRUCTION = """You are a perception system. Look at the image(s) given.
If multiple images are given, they are sequential frames from one video, in order.

Describe, in plain factual terms, what the media shows: subject matter, setting,
on-screen text or captions, mood/tone, visual style, people/objects present, and
any brand elements (logos, colors, product shots). If frames are from a video,
also describe how the scene changes across frames.

Respond with ONLY a JSON object, no prose, no markdown fences:
{
  "description": "a thorough paragraph describing what is shown",
  "on_screen_text": "any text visible in the media, verbatim, or empty string",
  "visual_style": "short phrase describing the visual/art style",
  "detected_elements": ["short", "list", "of", "notable", "objects/subjects"]
}"""


class GroqService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.groq_vision_model

    @staticmethod
    def _extract_json(text: str) -> dict:
        cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
        return json.loads(cleaned)

    def _perceive_sync(self, media_data_urls: list[str], caption: str | None) -> dict:
        content: list[dict] = [{"type": "text", "text": PERCEPTION_INSTRUCTION}]
        if caption:
            content.append({"type": "text", "text": f"Caption/context provided by the user: {caption}"})
        for url in media_data_urls:
            content.append({"type": "image_url", "image_url": {"url": url}})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        raw_text = response.choices[0].message.content or "{}"
        return self._extract_json(raw_text)

    async def perceive(self, media_data_urls: list[str], caption: str | None = None) -> dict:
        """
        media_data_urls: base64 data URLs (e.g. "data:image/jpeg;base64,...").
        For video, pass multiple frames extracted client-side, in order.
        """
        if not media_data_urls:
            raise ValueError("perceive() requires at least one image/frame")
        return await asyncio.to_thread(self._perceive_sync, media_data_urls, caption)
