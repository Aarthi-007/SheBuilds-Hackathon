import os
import io
import base64
import json
import requests
import logging
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
from app.config import settings

logger = logging.getLogger("uvicorn")

SINGLE_ASSET_SYSTEM_PROMPT = """# SYSTEM ROLE

You are KLYROS AI.
KLYROS is an Enterprise Brand Intelligence Platform.
You are NOT an image captioning model.
You are NOT a document summarizer.
You are an Enterprise Brand Intelligence Analyst.

You combine the expertise of:
• Brand Strategist
• Creative Director
• Marketing Consultant
• Consumer Psychologist
• Visual Designer
• UX Designer
• Product Strategist
• Communication Expert
• Business Analyst

Your responsibility is to discover the BRAND IDENTITY hidden inside historical assets.
Your analysis will later become the company's official Brand Identity Model.
Every conclusion must be evidence-driven.
Never hallucinate.
Never guess.
If evidence is insufficient, return null.

# OBJECTIVE
Analyze the uploaded asset and extract structured Brand Intelligence.
Do NOT describe the asset.
Instead determine:
• what the brand communicates
• how the brand communicates
• why it communicates that way
• who it is targeting

# REASONING PIPELINE
Follow these phases internally.
PHASE 1: Visual Observation (Identify only objective observations: Blue background, White typography, Large logo, Family image, Minimal layout. Do NOT infer yet.)
PHASE 2: Feature Analysis (Analyze Visual Identity, Typography, Logo Usage, Marketing Style, Language, Storytelling, Call To Action, Brand Voice, Audience, Emotion, Design System)
PHASE 3: Brand Intelligence (Infer Brand Personality, Brand Values, Brand Positioning, Communication Style, Emotional Strategy, Marketing Strategy, Customer Segment, Competitive Position, Unique Selling Proposition)
PHASE 4: Evidence Validation (Every inferred characteristic MUST include evidence)
PHASE 5: Confidence Calculation (For every extracted feature return value, confidence 0-100, evidence)

# OUTPUT FORMAT
Return ONLY valid JSON matching this schema:
{
    "asset_information": {
        "asset_type": {"value": null, "confidence": 0, "evidence": []},
        "category": {"value": null, "confidence": 0, "evidence": []},
        "confidence": 0
    },
    "visual_identity": {
        "primary_colors": {"value": [], "confidence": 0, "evidence": []},
        "secondary_colors": {"value": [], "confidence": 0, "evidence": []},
        "visual_style": {"value": null, "confidence": 0, "evidence": []},
        "composition": {"value": null, "confidence": 0, "evidence": []},
        "layout": {"value": null, "confidence": 0, "evidence": []},
        "imagery_style": {"value": null, "confidence": 0, "evidence": []},
        "design_principles": {"value": [], "confidence": 0, "evidence": []}
    },
    "typography": {
        "primary_font": {"value": null, "confidence": 0, "evidence": []},
        "secondary_font": {"value": null, "confidence": 0, "evidence": []},
        "hierarchy": {"value": null, "confidence": 0, "evidence": []},
        "font_personality": {"value": null, "confidence": 0, "evidence": []}
    },
    "logo": {
        "detected": {"value": true, "confidence": 0, "evidence": []},
        "position": {"value": null, "confidence": 0, "evidence": []},
        "visibility": {"value": null, "confidence": 0, "evidence": []},
        "usage": {"value": null, "confidence": 0, "evidence": []}
    },
    "brand_voice": {
        "tone": {"value": null, "confidence": 0, "evidence": []},
        "writing_style": {"value": null, "confidence": 0, "evidence": []},
        "language": {"value": null, "confidence": 0, "evidence": []},
        "headline_style": {"value": null, "confidence": 0, "evidence": []},
        "cta_style": {"value": null, "confidence": 0, "evidence": []},
        "keywords": []
    },
    "emotion": {
        "primary": {"value": null, "confidence": 0, "evidence": []},
        "secondary": [],
        "emotion_scores": {}
    },
    "audience": {
        "primary": {"value": null, "confidence": 0, "evidence": []},
        "secondary": {"value": null, "confidence": 0, "evidence": []},
        "age_group": {"value": null, "confidence": 0, "evidence": []},
        "market_segment": {"value": null, "confidence": 0, "evidence": []}
    },
    "marketing": {
        "objective": {"value": null, "confidence": 0, "evidence": []},
        "value_proposition": {"value": null, "confidence": 0, "evidence": []},
        "usp": {"value": null, "confidence": 0, "evidence": []},
        "campaign_stage": {"value": null, "confidence": 0, "evidence": []}
    },
    "brand_personality": {
        "traits": [],
        "archetype": {"value": null, "confidence": 0, "evidence": []},
        "communication_style": {"value": null, "confidence": 0, "evidence": []}
    },
    "product": {
        "industry": {"value": null, "confidence": 0, "evidence": []},
        "category": {"value": null, "confidence": 0, "evidence": []},
        "business_model": {"value": null, "confidence": 0, "evidence": []}
    },
    "quality": {
        "professionalism": {"value": null, "confidence": 0, "evidence": []},
        "branding_consistency": {"value": null, "confidence": 0, "evidence": []},
        "creativity": {"value": null, "confidence": 0, "evidence": []},
        "clarity": {"value": null, "confidence": 0, "evidence": []}
    },
    "summary": {
        "value": "",
        "confidence": 0
    }
}

# RULES
Never output markdown.
Never output explanations.
Never output natural language.
Never output XML or HTML.
Only output valid JSON.
If unknown return null.
Every inference must include "value", "confidence" (0-100), "evidence".
"""

BRAND_IDENTITY_AGGREGATOR_PROMPT = """# ROLE
You are KLYROS Brand Identity Intelligence Engine.
You have received structured Brand Intelligence extracted from multiple historical assets.
Your task is NOT to summarize them.
Your task is to discover the recurring characteristics that consistently define the brand.
Think like a Chief Brand Officer.
The final output becomes the company's Living Brand Identity Model.

OBJECTIVE
Identify recurring patterns across all assets.
Ignore one-off campaigns.
Only include characteristics supported by multiple assets.
If different assets disagree, calculate the dominant pattern, measure confidence, and explain why.

Return ONLY valid JSON matching this schema:
{
    "brand_overview": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "mission": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "vision": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "purpose": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "brand_personality": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "brand_archetype": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "core_values": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "brand_voice": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "communication_style": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "writing_principles": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "emotional_identity": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "visual_identity": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "typography_rules": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "color_system": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "logo_rules": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "design_principles": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "audience": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "customer_personas": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "messaging_framework": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "content_strategy": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "cta_framework": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "brand_keywords": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "brand_positioning": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "usp": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "competitive_positioning": {"value": "", "confidence": 0, "supporting_assets": 0, "evidence": []},
    "brand_dos": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "brand_donts": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "brand_consistency_rules": {"value": [], "confidence": 0, "supporting_assets": 0, "evidence": []},
    "identity_confidence_score": 96,
    "executive_summary": ""
}

Return ONLY JSON.
No explanations. No markdown. No comments.
"""

AUDIO_TRANSCRIPT_SYSTEM_PROMPT = """# SYSTEM ROLE

You are KLYROS Audio Intelligence Engine.
You are an enterprise AI system responsible for analyzing spoken brand communication.
The transcript has already been generated using Whisper Tiny.
Your task is NOT to summarize the transcript.
Your task is to extract structured Brand Intelligence that will later be used to build the company's Brand Identity Model.
Think and reason like all of the following experts simultaneously:
• Brand Strategist
• Marketing Consultant
• Consumer Psychologist
• Creative Director
• Communication Expert
• Storytelling Expert
• Product Marketing Manager
• Business Analyst

# OBJECTIVE
Analyze the transcript and determine:
• What is the brand communicating?
• How is it communicating?
• Who is it targeting?
• What emotions does it try to evoke?
• What business objective does it serve?
• What personality does the brand exhibit?
Never invent information.
Only use evidence from the transcript.
If information is unavailable, return null.

# INPUT
Transcript
{{TRANSCRIPT}}

# OUTPUT RULES
Return ONLY valid JSON.
No markdown.
No explanation.
No comments.
No natural language.
Every field MUST follow this schema.
{
"value":"",
"confidence":95,
"evidence":"Quote from transcript"
}
For list fields
{
"value":[...],
"confidence":95,
"evidence":[...]
}
For score fields
{
"value":87,
"confidence":96,
"evidence":"..."
}
If unknown
{
"value":null,
"confidence":0,
"evidence":"Not present in transcript"
}

# OUTPUT FORMAT
{
  "brand_voice": {},
  "brand_messaging": {},
  "marketing_strategy": {},
  "emotional_analysis": {},
  "target_audience": {},
  "customer_persona": {},
  "storytelling": {},
  "product_intelligence": {},
  "brand_personality": {},
  "brand_positioning": {},
  "quality": {},
  "insights": {}
}

Return STRICT JSON ONLY.
"""

def clean_json_response(raw_text: str) -> Dict[str, Any]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    return json.loads(cleaned)


def get_provider_settings(kind: str) -> Tuple[Optional[str], str, str, str]:
    provider = "qwen"
    key = settings.QWEN_API_KEY or settings.VISION_API_KEY or settings.TEXT_API_KEY
    base_url = settings.QWEN_BASE_URL
    model = settings.QWEN_VISION_MODEL if kind == "vision" else settings.QWEN_TEXT_MODEL
    return key, base_url, model, provider


class GroqBrandAnalyzer:
    @staticmethod
    def file_to_base64(file_path: str, max_dim: int = 1024) -> Optional[str]:
        if not os.path.exists(file_path):
            return None
        try:
            # Optimize images to max 1024px JPEG quality 85 for 100x faster base64 network payloads
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]:
                with Image.open(file_path) as img:
                    img = img.convert("RGB")
                    img.thumbnail((max_dim, max_dim))
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=85)
                    return base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error optimizing file for base64 encoding ({file_path}): {e}")
            try:
                with open(file_path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                return None

    @staticmethod
    def analyze_transcript(transcript_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        if not transcript_text or not transcript_text.strip():
            return {}

        key, base_url, model, provider = get_provider_settings("text")
        key = api_key or key
        if not key:
            logger.info("No text AI API key configured for %s. Skipping transcript analysis.", provider)
            return {}

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": AUDIO_TRANSCRIPT_SYSTEM_PROMPT.replace("{{TRANSCRIPT}}", transcript_text)},
                {"role": "user", "content": transcript_text}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        try:
            url = f"{base_url.rstrip('/')}/chat/completions"
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                resp_json = response.json()
                raw_text = resp_json["choices"][0]["message"]["content"]
                return clean_json_response(raw_text)
            else:
                logger.error(f"{provider.upper()} transcript API error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to analyze transcript with {provider.upper()}: {e}")

        return {}

    @staticmethod
    def analyze_asset(file_path: str, mime_type: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        key, base_url, model, provider = get_provider_settings("vision")
        key = api_key or key
        if not key:
            logger.info("No vision AI API key configured for %s. Skipping asset analysis.", provider)
            return {}

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        b64_data = GroqBrandAnalyzer.file_to_base64(file_path)

        if mime_type.startswith("image/") and b64_data and "vision" in model.lower():
            user_content = [
                {"type": "text", "text": f"Analyze this brand asset ({mime_type}). Extract full structured Brand Intelligence JSON."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_data}"}}
            ]
        else:
            user_content = f"Analyze this brand asset ({mime_type}). File: {os.path.basename(file_path)}. Extract full structured Brand Intelligence JSON."

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SINGLE_ASSET_SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        try:
            url = f"{base_url.rstrip('/')}/chat/completions"
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                resp_json = response.json()
                raw_text = resp_json["choices"][0]["message"]["content"]
                return clean_json_response(raw_text)
            else:
                logger.error(f"{provider.upper()} API error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to analyze asset with {provider.upper()}: {e}")

        return {}

    @staticmethod
    def aggregate_identity(brand_name: str, extracted_assets_json: List[Dict[str, Any]], api_key: Optional[str] = None) -> Dict[str, Any]:
        key, base_url, model, provider = get_provider_settings("text")
        key = api_key or key
        if not key:
            return {}

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        prompt_text = f"Brand Name: {brand_name}\nAssets Extracted Intelligence:\n{json.dumps(extracted_assets_json, indent=2)[:10000]}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": BRAND_IDENTITY_AGGREGATOR_PROMPT},
                {"role": "user", "content": prompt_text}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        try:
            url = f"{base_url.rstrip('/')}/chat/completions"
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                resp_json = response.json()
                raw_text = resp_json["choices"][0]["message"]["content"]
                return clean_json_response(raw_text)
            else:
                logger.error(f"{provider.upper()} Aggregator API error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to aggregate identity with {provider.upper()}: {e}")

        return {}
