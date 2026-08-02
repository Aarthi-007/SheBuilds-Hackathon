"""
Thin wrapper around the Anthropic SDK.

Per project rule 1: only Services talk to Claude directly. Agents call
this service; routes never touch it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from anthropic import AsyncAnthropic

from backend.config.settings import get_settings

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class ClaudeService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.claude_model

    def _load_prompt(self, prompt_name: str, variables: dict) -> str:
        template = (PROMPTS_DIR / prompt_name).read_text(encoding="utf-8")
        for key, value in variables.items():
            template = template.replace("{{" + key + "}}", "" if value is None else str(value))
        return template

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Claude sometimes wraps JSON in ```json fences despite instructions; strip them."""
        cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
        return json.loads(cleaned)

    async def research_and_reason(self, prompt_name: str, variables: dict) -> dict:
        """
        Calls Claude with the web_search tool enabled so it can research
        current trends before reasoning. Returns the parsed JSON payload
        from the model's final text response.
        """
        prompt = self._load_prompt(prompt_name, variables)

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=4000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )

        text_blocks = [block.text for block in response.content if block.type == "text"]
        final_text = text_blocks[-1] if text_blocks else ""

        try:
            return self._extract_json(final_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Claude did not return valid JSON for prompt '{prompt_name}': {exc}\n"
                f"Raw output: {final_text[:500]}"
            ) from exc
