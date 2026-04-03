import json
from typing import Any, Dict

from app.models.enums import IssueType, Severity
from app.schemas.common import AnalysisIssue, AnalysisResult, BillingRecord
from app.services.openai_service import OpenAIService
from app.tools.llm_reasoning_tool import LLMReasoningTool


class FakeResponse:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Dict[str, Any]:
        return self.payload


class FakeOpenAIClient:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self.payload = payload
        self.calls: int = 0

    def post(self, url: str, *, headers: Dict[str, str], json: Dict[str, Any], timeout: float) -> FakeResponse:
        self.calls += 1
        return FakeResponse(self.payload)


def test_openai_service_parses_valid_response():
    payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "issues": [
                                {
                                    "id": "r_001",
                                    "issue": "RATE_MISMATCH",
                                    "expected_amount": 1000.0,
                                    "billed_amount": 920.0,
                                    "leakage": 80.0,
                                    "severity": "HIGH",
                                    "reasoning": "Rate is lower than contract.",
                                    "suggestion": "Update the billed rate.",
                                    "confidence_score": 0.97,
                                }
                            ],
                            "summary_reasoning": "Clear rate mismatch leading to underbilling.",
                            "overall_confidence_score": 0.97,
                        }
                    )
                }
            }
        ]
    }
    client = FakeOpenAIClient(payload)
    service = OpenAIService(client=client, api_key="test-key", model="test-model")

    record = BillingRecord(contract_id="C-001")
    issues = [
        AnalysisIssue(
            issue=IssueType.RATE_MISMATCH.value,
            reasoning="Rate mismatch detected",
            severity=Severity.HIGH.value,
            leakage=80.0,
        )
    ]
    result = service.analyze(record, issues, computed_values={}, missing_fields=[])

    assert result["summary_reasoning"] == "Clear rate mismatch leading to underbilling."
    assert result["overall_confidence_score"] == 0.97
    assert client.calls == 1


def test_openai_service_fallback_on_invalid_body():
    payload = {"choices": [{"message": {"content": "not-json"}}]}
    service = OpenAIService(client=FakeOpenAIClient(payload), api_key="test-key", model="test-model")
    record = BillingRecord(contract_id="C-001")
    issues = []
    result = service.analyze(record, issues, computed_values={}, missing_fields=[])
    assert result == {}


def test_llm_reasoning_tool_uses_openai_and_fallback():
    payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "issues": [],
                            "summary_reasoning": "OpenAI reasoning",
                            "overall_confidence_score": 0.9,
                            "analyzer_type": "RULE_PLUS_LLM",
                        }
                    )
                }
            }
        ]
    }
    client = FakeOpenAIClient(payload)
    openai_service = OpenAIService(client=client, api_key="test-key", model="test-model")
    tool = LLMReasoningTool(openai_service=openai_service)

    result = AnalysisResult(
        record_id="r_001",
        issues=[
            AnalysisIssue(
                issue=IssueType.RATE_MISMATCH.value,
                reasoning="Rate mismatch detected",
                severity=Severity.HIGH.value,
                leakage=80.0,
            )
        ],
        has_leakage=True,
        total_leakage_amount=80.0,
        analysis_status="COMPLETED",
        analyzer_type="RULE_ONLY",
        analysis_version=1,
    )
    record = BillingRecord(contract_id="C-001")

    llm_payload = tool.call_llm(record, result)
    assert llm_payload["summary_reasoning"] == "OpenAI reasoning"
    assert client.calls == 1

    empty_service = OpenAIService(client=FakeOpenAIClient(payload={}), api_key=None, model="unused")
    tool_fallback = LLMReasoningTool(openai_service=empty_service)
    fallback_payload = tool_fallback.call_llm(record, result)
    assert fallback_payload["summary_reasoning"] == "Rate mismatch detected"
