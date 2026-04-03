from __future__ import annotations

from typing import Any, Dict, List

from ..schemas.common import AnalysisIssue, AnalysisResult, BillingRecord
from ..services.openai_service import OpenAIService


class LLMReasoningTool:
    """
    Wrapper around OpenAIService with a safe fallback.
    """

    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self._openai = openai_service or OpenAIService()

    def should_call_llm(self, result: AnalysisResult) -> bool:
        # Call LLM only when there is leakage and at least one deterministic issue.
        return result.has_leakage and len(result.issues) > 0

    def call_llm(
        self,
        record: BillingRecord,
        result: AnalysisResult,
        *,
        computed_values: Dict[str, Any] | None = None,
        missing_fields: List[str] | None = None,
    ) -> Dict[str, Any]:
        """
        Call OpenAI (or return a deterministic fallback) to enrich analysis metadata.
        """
        computed_values = computed_values or {}
        missing_fields = missing_fields or []

        openai_payload = self._openai.analyze(
            record=record,
            issues=result.issues,
            computed_values=computed_values,
            missing_fields=missing_fields,
        )

        if not openai_payload:
            primary_issue = result.issues[0] if result.issues else None
            return {
                "summary_reasoning": (
                    primary_issue.message if primary_issue else "No significant issues detected for this record."
                ),
                "suggestion": "Review the contract and invoice for discrepancies and adjust billing if necessary.",
                "analyzer_type": "RULE_PLUS_LLM",
            }

        return openai_payload

