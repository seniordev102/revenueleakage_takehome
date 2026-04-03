from datetime import date

from app.agents.leakage_agent import LeakageAnalysisAgent
from app.models.enums import IssueType, Severity
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.record_repository import RecordRepository
from app.schemas.common import AnalysisIssue, AnalysisResult, BillingRecord
from app.services.dynamodb_service import DynamoDBService
from app.tools.llm_reasoning_tool import LLMReasoningTool


class FakeClient:
    def __init__(self) -> None:
        self.put_calls: list[dict] = []
        self.update_calls: list[dict] = []

    def put_item(self, *, TableName, Item):
        self.put_calls.append({"TableName": TableName, "Item": Item})

    def update_item(self, *, TableName, Key, UpdateExpression, ExpressionAttributeNames, ExpressionAttributeValues):
        self.update_calls.append(
            {
                "TableName": TableName,
                "Key": Key,
                "UpdateExpression": UpdateExpression,
                "ExpressionAttributeNames": ExpressionAttributeNames,
                "ExpressionAttributeValues": ExpressionAttributeValues,
            }
        )


class FakeLLMTool(LLMReasoningTool):
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def should_call_llm(self, result: AnalysisResult) -> bool:
        return result.has_leakage

    def call_llm(self, record: BillingRecord, result: AnalysisResult):
        self.calls.append({"record_id": record.record_id, "total_leakage": result.total_leakage_amount})
        return {
            "issues": [
                {
                    "issue_type": IssueType.RATE_MISMATCH.value,
                    "severity": Severity.HIGH.value,
                    "reasoning": "Contract rate exceeds the billed rate, causing underbilling.",
                    "suggestion": "Update the invoice rate to match the contract and recover the shortfall.",
                    "confidence_score": 0.97,
                }
            ],
            "summary_reasoning": "Mock reasoning",
            "suggestion": "Mock suggestion",
            "analyzer_type": "RULE_PLUS_LLM",
        }


def make_agent() -> tuple[LeakageAnalysisAgent, FakeClient, FakeLLMTool]:
    client = FakeClient()
    dynamo = DynamoDBService(table_name="RevenueLeakage", client=client)
    record_repo = RecordRepository(dynamo)
    analysis_repo = AnalysisRepository(dynamo)
    llm_tool = FakeLLMTool()
    agent = LeakageAnalysisAgent(record_repo, analysis_repo, llm_tool=llm_tool)
    return agent, client, llm_tool


def test_agent_orchestrates_tools_and_updates_repositories():
    agent, client, llm_tool = make_agent()

    record = BillingRecord(
        upload_id="u_001",
        record_id="r_001",
        contract_id="C-001",
        customer_id="CU-100",
        product_id="P-101",
        agreed_rate=100,
        billed_rate=92,
        quantity=10,
        expected_amount=1000,
        billed_amount=920,
        discount=0,
        tax=0,
        currency="USD",
        billing_date=date(2026, 3, 25),
        contract_start_date=date(2026, 1, 1),
        contract_end_date=date(2026, 12, 31),
        region="US",
    )

    result = agent.analyze_record("u_001", record)

    assert result.record_id == "r_001"
    assert result.has_leakage is True
    assert result.total_leakage_amount == 80.0
    assert any(i.issue == "RATE_MISMATCH" for i in result.issues)
    assert result.issues[0].id == "r_001"
    assert result.issues[0].expected_amount == 1000
    assert result.issues[0].billed_amount == 920
    assert result.issues[0].leakage == 80.0
    assert result.issues[0].reasoning == "Contract rate exceeds the billed rate, causing underbilling."
    assert result.issues[0].suggestion == "Update the invoice rate to match the contract and recover the shortfall."
    assert result.analyzer_type == "RULE_PLUS_LLM"

    # One analysis item written, one record summary update
    assert len(client.put_calls) >= 1
    assert len(client.update_calls) == 1

    # LLM should have been called once for leaking record
    assert len(llm_tool.calls) == 1
    assert llm_tool.calls[0]["record_id"] == "r_001"


def test_agent_skips_llm_when_no_leakage():
    agent, client, llm_tool = make_agent()

    record = BillingRecord(
        upload_id="u_clean",
        record_id="r_clean",
        contract_id="C-011",
        customer_id="CU-110",
        product_id="P-111",
        agreed_rate=75,
        billed_rate=75,
        quantity=4,
        expected_amount=300,
        billed_amount=300,
        discount=0,
        tax=0,
        currency="USD",
        billing_date=date(2026, 3, 5),
        contract_start_date=date(2026, 1, 1),
        contract_end_date=date(2026, 12, 31),
        region="US",
    )

    result = agent.analyze_record("u_clean", record)

    assert result.has_leakage is False
    assert result.total_leakage_amount == 0.0
    assert result.analyzer_type == "RULE_ONLY" or result.analyzer_type == "RULE_PLUS_LLM"
    assert len(llm_tool.calls) == 0


def test_agent_primary_issue_type_derivation_prefers_high_severity():
    # Directly test the helper with mixed severities
    issues = [
        AnalysisIssue(
            issue=IssueType.EXPECTED_VS_BILLED_DIFFERENCE.value,
            reasoning="Medium issue",
            severity=Severity.MEDIUM.value,
            leakage=50.0,
        ),
        AnalysisIssue(
            issue=IssueType.RATE_MISMATCH.value,
            reasoning="High issue",
            severity=Severity.HIGH.value,
            leakage=80.0,
        ),
    ]
    agent, _, _ = make_agent()
    primary = agent._derive_primary_issue_type(issues)
    assert primary == IssueType.RATE_MISMATCH

