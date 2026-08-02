"""
ClaudeService — wraps the Anthropic SDK. Only the method this layer needs is shown below;
the rest of ClaudeService (extract_brand_identity, enrich_perception, etc.) lives with the
other agents and is unchanged by this layer.
"""

from pathlib import Path
from anthropic import AsyncAnthropic
from pydantic import BaseModel

from config.settings import settings

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class ClaudeService:
    def __init__(self):
        self._client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    def _load_prompt(self, filename: str, variables: dict) -> str:
        template = (PROMPTS_DIR / filename).read_text()
        for key, value in variables.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        return template

    async def generate_structured(self, prompt_file: str, variables: dict, schema: type[BaseModel]) -> BaseModel:
        """Load a prompt markdown file, template it, call Claude, validate the JSON reply against `schema`."""
        prompt = self._load_prompt(prompt_file, variables)
        response = await self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = "".join(block.text for block in response.content if block.type == "text")
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        return schema.model_validate_json(cleaned)
