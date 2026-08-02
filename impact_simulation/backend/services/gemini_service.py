"""
Wraps the Google Gemini API for image perception.

Gemini 2.5 Flash handles multimodal image understanding — it converts
a raw image into structured text. No agent or service downstream touches
raw media; everything works off the text description this produces.
"""

from __future__ import annotations

import base64
import json
import re

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from backend.config.settings import get_settings

PERCEPTION_INSTRUCTION = """You are a perception system. Look at the image provided.

Describe in plain factual terms what the image shows: subject matter, setting,
on-screen text or captions, mood/tone, visual style, people/objects present,
and any brand elements (logos, colors, product shots).

Respond with ONLY a JSON object, no prose, no markdown fences:
{
  "description": "a thorough paragraph describing what is shown",
  "on_screen_text": "any text visible in the image, verbatim, or empty string",
  "visual_style": "short phrase describing the visual/art style",
  "detected_elements": ["short", "list", "of", "notable", "objects/subjects"]
}"""


class GeminiService:
    def __init__(self) -> None:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(
            model_name=settings.gemini_vision_model,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )

    @staticmethod
    def _extract_json(text: str) -> dict:
        cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
        return json.loads(cleaned)

    @staticmethod
    def _data_url_to_part(data_url: str) -> dict:
        """Convert a base64 data URL into a Gemini inline_data part."""
        # data_url format: "data:<mime_type>;base64,<data>"
        header, encoded = data_url.split(",", 1)
        mime_type = header.split(":")[1].split(";")[0]
        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": encoded,
            }
        }

    async def perceive(self, media_data_urls: list[str], caption: str | None = None) -> dict:
        """
        media_data_urls: list with exactly one base64 data URL for an image.
        Returns a structured perception dict.
        """
        if not media_data_urls:
            raise ValueError("perceive() requires at least one image")

        parts: list = [PERCEPTION_INSTRUCTION]
        if caption:
            parts.append(f"Caption/context provided by the user: {caption}")
        for url in media_data_urls:
            parts.append(self._data_url_to_part(url))

        response = await self._model.generate_content_async(
            parts,
            generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
        )
        raw_text = response.text or "{}"
        try:
            return self._extract_json(raw_text)
        except json.JSONDecodeError:
            return {"description": raw_text, "on_screen_text": "", "visual_style": "", "detected_elements": []}
