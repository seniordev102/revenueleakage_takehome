from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import httpx

from ..core.logging import get_logger
from ..core.settings import get_settings
from ..schemas.common import AnalysisIssue, BillingRecord

logger = get_logger(__name__)

class OpenAIService:
    """
    Thin wrapper around the OpenAI chat completions API.

    For unit tests we inject a fake HTTP client that returns a predefined JSON body.
    In real usage, the service reads the API key from OPENAI_API_KEY.
    """

    def __init__(
        self,
        *,
        client: Any | None = None,
        api_key: str | None = None,
        model: str | None = None,
        prompt_path: str | Path | None = None,
    ) -> None:
        settings = get_settings()
        self._client = client or httpx.Client(timeout=settings.openai_timeout_seconds)
        self._api_key = api_key if api_key is not None else settings.openai_api_key
        self._model = model or settings.openai_model
        self._base_url = settings.openai_base_url
        self._timeout = settings.openai_timeout_seconds
        self._prompt_path = Path(prompt_path) if prompt_path else Path(__file__).resolve().parents[3] / "openai-prompt.md"

    def analyze(
        self,
        record: BillingRecord,
        issues: List[AnalysisIssue],
        computed_values: Dict[str, Any],
        missing_fields: List[str],
    ) -> Dict[str, Any]:
        if not self._api_key:
            logger.info("OpenAI API key not configured; using deterministic fallback")
            return {}

        prompt = self._build_prompt(record, issues, computed_values, missing_fields)
        system_prompt = self._load_system_prompt()

        try:
            response = self._client.post(
                self._base_url,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=float(self._timeout),
            )
            if hasattr(response, "raise_for_status"):
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("OpenAI request failed: %s", exc)
            return {}
        except Exception as exc:
            logger.warning("Unexpected OpenAI integration failure: %s", exc)
            return {}

        return self._parse_response(response)

    @staticmethod
    def _build_prompt(
        record: BillingRecord,
        issues: List[AnalysisIssue],
        computed_values: Dict[str, Any],
        missing_fields: List[str],
    ) -> str:
        payload = {
            "record": record.model_dump(mode="json"),
            "deterministic_findings": [i.model_dump(mode="json") for i in issues],
            "computed_values": computed_values,
            "missing_fields": missing_fields,
        }
        return json.dumps(payload)

    def _load_system_prompt(self) -> str:
        try:
            return self._prompt_path.read_text(encoding="utf-8")
        except OSError:
            return (
                "You are an AI reasoning component inside a revenue leakage detection platform. "
                "Return strict JSON only with issue reasoning and suggestions."
            )

    @staticmethod
    def _parse_response(response: Any) -> Dict[str, Any]:
        try:
            body = response.json() if hasattr(response, "json") else response
        except Exception:
            return {}

        if not isinstance(body, dict):
            return {}

        choices = body.get("choices")
        if not isinstance(choices, list) or not choices:
            return {}

        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str):
            return {}

        try:
            parsed = json.loads(content)
        except Exception:
            return {}

        return parsed if isinstance(parsed, dict) else {}
