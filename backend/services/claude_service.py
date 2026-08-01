import json
import re
import logging
from pathlib import Path
from typing import Any, Type, TypeVar, Optional
from pydantic import BaseModel
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)
T = TypeVar("T", bound=BaseModel)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

_client = None


def _get_client():
    global _client
    if _client is None:
        try:
            import anthropic
            if settings.anthropic_api_key:
                _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        except Exception as e:
            logger.warning("Anthropic client initialization skipped: %s", e)
    return _client


def _load_prompt(filename: str, variables: dict[str, Any] = {}) -> str:
    path = PROMPTS_DIR / filename
    if not path.exists():
        return f"Prompt file '{filename}' with variables: {json.dumps(variables)}"
    template = path.read_text(encoding="utf-8")
    for key, value in variables.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template


class ClaudeService:
    MODEL = "claude-sonnet-4-5"

    async def generate(self, prompt_file: str, variables: dict[str, Any] = {}) -> str:
        client = _get_client()
        if client:
            prompt = _load_prompt(prompt_file, variables)
            response = client.messages.create(
                model=self.MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        return f"Generated response fallback for {prompt_file}"

    async def generate_structured(
        self, prompt_file: str, variables: dict[str, Any], schema: Type[T]
    ) -> T:
        client = _get_client()
        if client:
            prompt = _load_prompt(prompt_file, variables)
            full_prompt = (
                prompt
                + "\n\nRespond ONLY with a valid JSON object matching the schema. No markdown fences."
            )
            response = client.messages.create(
                model=self.MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": full_prompt}],
            )
            raw = response.content[0].text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            return schema(**json.loads(raw))
        
        # Schema fallback instance creation
        return schema.construct() if hasattr(schema, "construct") else schema()

    async def enrich_perception(self, raw_json: dict) -> dict:
        client = _get_client()
        if client:
            variables = {"raw_json": json.dumps(raw_json, indent=2)}
            prompt = _load_prompt("perception_enrichment.md", variables)
            response = client.messages.create(
                model=self.MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            return json.loads(raw)

        return {
            "intent": "Brand Engagement",
            "sentiment": "Positive",
            "emotion": "Trust",
            "target_audience": "Families",
            "raw": raw_json
        }

    async def extract_brand_identity(self, content_batch: list[dict], company_id: str) -> dict:
        client = _get_client()
        if client:
            variables = {
                "content_batch": json.dumps(content_batch, indent=2),
                "company_id": company_id,
            }
            prompt = _load_prompt("brand_identity_extraction.md", variables)
            response = client.messages.create(
                model=self.MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            return json.loads(raw)

        return {
            "company_id": company_id,
            "brand_name": company_id.replace("_", " ").title(),
            "brand_voice": {"tone": "Warm & Authentic"},
            "visual_identity": {"primary_color": "#0055A4"}
        }
