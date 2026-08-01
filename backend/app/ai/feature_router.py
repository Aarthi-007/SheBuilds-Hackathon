import os
import time
import logging
from typing import Any, Dict, List, Optional
from app.ai.groq_analyzer import GroqBrandAnalyzer
from app.ai.model_manager import model_manager
from app.config import settings

logger = logging.getLogger("uvicorn")

FEATURE_MODEL_MAP: Dict[str, str] = {
    "dominant_colors": "qwen",
    "color_palette": "qwen",
    "visual_style": "qwen",
    "layout": "qwen",
    "composition": "qwen",
    "logo": "qwen",
    "logo_position": "qwen",
    "branding_elements": "qwen",
    "emotion": "qwen",
    "audience": "qwen",
    "brand_personality": "qwen",
    "tone": "qwen",
    "brand_voice": "qwen",
    "marketing_strategy": "qwen",
    "value_proposition": "qwen",
    "cta": "ocr",
    "headline": "ocr",
    "body_text": "ocr",
    "tagline": "ocr",
    "keywords": "ocr",
    "pdf_text": "pymupdf",
    "ocr_text": "ocr",
    "transcript": "whisper",
    "voice_emotion": "qwen",
    "speaker_style": "qwen",
    "embedding": "sentence_transformer"
}

ASSET_FEATURES: Dict[str, List[str]] = {
    "image": [
        "dominant_colors",
        "color_palette",
        "visual_style",
        "layout",
        "composition",
        "logo",
        "logo_position",
        "branding_elements",
        "emotion",
        "audience",
        "brand_personality",
        "tone",
        "brand_voice",
        "marketing_strategy",
        "value_proposition",
        "cta",
        "headline",
        "body_text",
        "tagline",
        "keywords",
        "ocr_text",
        "embedding"
    ],
    "audio": [
        "transcript",
        "voice_emotion",
        "speaker_style",
        "brand_voice",
        "emotion",
        "audience",
        "marketing_strategy",
        "value_proposition",
        "embedding"
    ],
    "video": [
        "transcript",
        "voice_emotion",
        "speaker_style",
        "brand_voice",
        "emotion",
        "audience",
        "marketing_strategy",
        "value_proposition",
        "dominant_colors",
        "color_palette",
        "visual_style",
        "layout",
        "composition",
        "logo",
        "logo_position",
        "branding_elements",
        "embedding"
    ],
    "pdf": [
        "pdf_text",
        "ocr_text",
        "headline",
        "body_text",
        "tagline",
        "keywords",
        "cta",
        "tone",
        "brand_voice",
        "emotion",
        "audience",
        "marketing_strategy",
        "value_proposition",
        "layout",
        "composition",
        "visual_style",
        "logo",
        "logo_position",
        "branding_elements",
        "embedding"
    ],
    "website": [
        "ocr_text",
        "headline",
        "body_text",
        "tagline",
        "keywords",
        "cta",
        "tone",
        "brand_voice",
        "emotion",
        "audience",
        "marketing_strategy",
        "value_proposition",
        "layout",
        "composition",
        "visual_style",
        "branding_elements",
        "embedding"
    ],
    "text": [
        "headline",
        "body_text",
        "tagline",
        "keywords",
        "cta",
        "tone",
        "brand_voice",
        "emotion",
        "audience",
        "marketing_strategy",
        "value_proposition",
        "embedding"
    ]
}


class FeatureRouter:
    """Routes feature requests to the correct AI model and normalizes the outputs."""

    @classmethod
    async def extract_features_for_asset(
        cls,
        asset: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        asset_type = asset.get("asset_type", "image").lower()
        storage_path = asset.get("storage_path", "")
        features: List[Dict[str, Any]] = []

        raw_data = await cls._extract_raw_data(asset, api_key=api_key)
        qwen_payload = cls._prepare_qwen_payload(asset, raw_data, api_key=api_key)

        feature_names = ASSET_FEATURES.get(asset_type, list(FEATURE_MODEL_MAP.keys()))
        for feature_name in feature_names:
            model_name = FEATURE_MODEL_MAP.get(feature_name)
            if not model_name:
                continue

            start = time.time()
            value = cls._extract_feature_value(feature_name, model_name, raw_data, qwen_payload)
            elapsed_ms = round((time.time() - start) * 1000, 2)
            confidence = cls._confidence_for_value(model_name, value)
            model = model_name
            source = cls._source_for_feature(feature_name, asset_type)
            evidence = cls._evidence_for_feature(feature_name, model_name, raw_data)

            features.append({
                "feature_name": feature_name,
                "value": value,
                "confidence": confidence,
                "model": model,
                "source_model": model,
                "source": source,
                "evidence": evidence,
                "processing_time_ms": elapsed_ms
            })

            logger.info(
                "Feature %s -> %s -> %dms -> %d%%",
                feature_name,
                "PaddleOCR" if model_name == "ocr" else ("SentenceTransformer" if model_name == "sentence_transformer" else model_name.capitalize()),
                int(elapsed_ms),
                int(confidence)
            )

        return features

    @classmethod
    async def _extract_raw_data(cls, asset: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        asset_type = asset.get("asset_type", "image").lower()
        storage_path = asset.get("storage_path", "")
        metadata = asset.get("metadata", {}) or {}
        raw_text = ""
        ocr_text = None
        pdf_text = None
        transcript = None

        if asset_type in ["image", "pdf", "website"] and storage_path:
            ocr_text = await cls._extract_ocr_text(storage_path)

        if asset_type == "pdf" and storage_path:
            pdf_text = await cls._extract_pymupdf_text(storage_path)
            if not pdf_text and ocr_text:
                pdf_text = ocr_text

        if asset_type == "audio" and storage_path:
            transcript = await cls._extract_whisper_transcript(storage_path)

        if asset_type == "video" and storage_path:
            transcript = await cls._extract_whisper_transcript(storage_path)

        if asset_type in ["website", "text"]:
            raw_text = metadata.get("extracted_text") or metadata.get("description") or asset.get("filename") or ""

        if not raw_text:
            raw_text = transcript or pdf_text or ocr_text or ""

        return {
            "asset_type": asset_type,
            "storage_path": storage_path,
            "ocr_text": ocr_text,
            "pdf_text": pdf_text,
            "transcript": transcript,
            "text": raw_text,
            "metadata": metadata
        }

    @classmethod
    def _prepare_qwen_payload(
        cls,
        asset: Dict[str, Any],
        raw_data: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        if raw_data.get("asset_type") == "image" and raw_data.get("storage_path") and os.path.exists(raw_data["storage_path"]):
            return GroqBrandAnalyzer.analyze_asset(raw_data["storage_path"], asset.get("mime_type", "image/jpeg"), api_key=api_key)

        if raw_data.get("text"):
            return GroqBrandAnalyzer.analyze_transcript(raw_data["text"], api_key=api_key)

        return {}

    @classmethod
    def _extract_feature_value(
        cls,
        feature_name: str,
        model_name: str,
        raw_data: Dict[str, Any],
        qwen_payload: Dict[str, Any]
    ) -> Any:
        if model_name == "qwen":
            return cls._extract_qwen_feature(feature_name, qwen_payload)
        if model_name == "whisper":
            return cls._extract_whisper_feature(feature_name, raw_data)
        if model_name == "ocr":
            return cls._extract_ocr_feature(feature_name, raw_data)
        if model_name == "pymupdf":
            return cls._extract_pymupdf_feature(feature_name, raw_data)
        if model_name == "sentence_transformer":
            return cls._extract_embedding_feature(feature_name, raw_data, qwen_payload)
        return None

    @classmethod
    def _extract_qwen_feature(cls, feature_name: str, qwen_payload: Dict[str, Any]) -> Any:
        if not qwen_payload:
            return None
        if feature_name in qwen_payload:
            return qwen_payload[feature_name]

        fallback_map = {
            "brand_voice": ["brand_voice", "tone", "voice"],
            "emotion": ["emotion", "sentiment"],
            "audience": ["audience", "target_audience", "customer_persona"],
            "brand_personality": ["brand_personality", "personality"],
            "marketing_strategy": ["marketing_strategy", "strategy"],
            "value_proposition": ["value_proposition", "positioning"],
            "cta": ["cta", "call_to_action"],
            "visual_style": ["visual_style", "visual_identity"],
            "layout": ["layout", "composition"],
            "branding_elements": ["branding_elements", "brand_elements"],
            "logo_position": ["logo_position", "logo_location"],
            "dominant_colors": ["dominant_colors", "primary_colors", "color_palette"],
            "color_palette": ["color_palette", "primary_colors"],
            "logo": ["logo", "brand_logo"],
            "speaker_style": ["speaker_style"],
            "voice_emotion": ["voice_emotion", "emotion"],
            "tone": ["tone", "brand_voice"]
        }

        for key in fallback_map.get(feature_name, []):
            if key in qwen_payload:
                return qwen_payload[key]

        return None

    @classmethod
    def _extract_whisper_feature(cls, feature_name: str, raw_data: Dict[str, Any]) -> Any:
        if feature_name != "transcript":
            return None
        return raw_data.get("transcript")

    @classmethod
    def _extract_ocr_feature(cls, feature_name: str, raw_data: Dict[str, Any]) -> Any:
        ocr_text = raw_data.get("ocr_text")
        if not ocr_text:
            return None

        if feature_name == "ocr_text":
            return ocr_text
        if feature_name == "headline":
            return cls._select_headline_from_text(ocr_text)
        if feature_name == "body_text":
            return ocr_text.strip()
        if feature_name == "tagline":
            return cls._select_tagline_from_text(ocr_text)
        if feature_name == "keywords":
            return None
        if feature_name == "cta":
            return None
        return None

    @classmethod
    def _extract_pymupdf_feature(cls, feature_name: str, raw_data: Dict[str, Any]) -> Any:
        if feature_name != "pdf_text":
            return None
        return raw_data.get("pdf_text")

    @classmethod
    def _extract_embedding_feature(
        cls,
        feature_name: str,
        raw_data: Dict[str, Any],
        qwen_payload: Dict[str, Any]
    ) -> Any:
        if feature_name != "embedding":
            return None

        # Multimodal Embedding Fusion: Combine transcript, OCR text, PDF text, and Qwen features into a unified fusion representation
        fusion_parts: List[str] = []
        if raw_data.get("transcript"):
            fusion_parts.append(f"Transcript: {raw_data['transcript']}")
        if raw_data.get("ocr_text"):
            fusion_parts.append(f"OCR: {raw_data['ocr_text']}")
        if raw_data.get("pdf_text"):
            fusion_parts.append(f"PDF: {raw_data['pdf_text']}")

        if qwen_payload and isinstance(qwen_payload, dict):
            for k in ["brand_voice", "visual_style", "marketing_strategy", "value_proposition", "emotion", "brand_personality"]:
                if qwen_payload.get(k):
                    fusion_parts.append(f"{k}: {qwen_payload[k]}")

        if not fusion_parts and raw_data.get("text"):
            fusion_parts.append(str(raw_data["text"]))

        fused_text = " | ".join(fusion_parts).strip()
        if not fused_text:
            return None

        return model_manager._get_embedding_sync(fused_text)

    @classmethod
    def _select_headline_from_text(cls, text: str) -> Optional[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return None
        return lines[0] if len(lines[0]) <= 120 else lines[0][:120].strip()

    @classmethod
    def _select_tagline_from_text(cls, text: str) -> Optional[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) > 1:
            return lines[1] if len(lines[1]) <= 80 else lines[1][:80].strip()
        return None

    @classmethod
    def _confidence_for_value(cls, model_name: str, value: Any) -> float:
        if value is None:
            return 0.0
        if model_name == "whisper":
            return 90.0
        if model_name == "ocr":
            return 88.0
        if model_name == "pymupdf":
            return 92.0
        if model_name == "sentence_transformer":
            return 95.0
        if model_name == "qwen":
            return 85.0
        return 75.0

    @classmethod
    def _source_for_feature(cls, feature_name: str, asset_type: str) -> str:
        return asset_type

    @classmethod
    def _evidence_for_feature(cls, feature_name: str, model_name: str, raw_data: Dict[str, Any]) -> str:
        if model_name == "ocr":
            return "PaddleOCR extracted visible text"
        if model_name == "pymupdf":
            return "PyMuPDF extracted selectable PDF text"
        if model_name == "whisper":
            return "Whisper audio transcription"
        if model_name == "sentence_transformer":
            return "SentenceTransformer semantic embedding"
        if model_name == "qwen":
            return "Qwen brand intelligence reasoning"
        return "AI feature extraction"

    @classmethod
    async def _extract_ocr_text(cls, file_path: str) -> Optional[str]:
        ocr_model = model_manager.get_model("ocr")
        if ocr_model is None or not os.path.exists(file_path):
            return None

        try:
            ocr_res = ocr_model.ocr(file_path, cls=True)
            lines: List[str] = []
            if isinstance(ocr_res, list):
                for block in ocr_res:
                    if block:
                        for line in block:
                            if line and len(line) >= 2:
                                lines.append(line[1][0])
            return "\n".join(lines).strip()
        except Exception as e:
            logger.error("PaddleOCR extraction error on '%s': %s", file_path, e)
            return None

    @classmethod
    async def _extract_pymupdf_text(cls, file_path: str) -> Optional[str]:
        fitz_lib = model_manager.get_model("pymupdf")
        if fitz_lib is None or not os.path.exists(file_path):
            return None

        try:
            doc = fitz_lib.open(file_path)
            text_pages = [page.get_text() for page in doc]
            doc.close()
            return "\n".join(text_pages).strip()
        except Exception as e:
            logger.error("PyMuPDF extraction error on '%s': %s", file_path, e)
            return None

    @classmethod
    async def _extract_whisper_transcript(cls, file_path: str) -> Optional[str]:
        whisper_model = model_manager.get_model("whisper")
        if whisper_model is None or not os.path.exists(file_path):
            return None

        try:
            result = whisper_model.transcribe(file_path)
            text = result.get("text") if isinstance(result, dict) else None
            return text.strip() if isinstance(text, str) else None
        except Exception as e:
            logger.error("Whisper transcription error on '%s': %s", file_path, e)
            return None
