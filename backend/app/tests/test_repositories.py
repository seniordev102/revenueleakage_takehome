from datetime import date

from app.models.enums import IssueType, Severity
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.record_repository import RecordRepository
from app.repositories.upload_repository import UploadRepository
from app.schemas.common import AnalysisIssue, AnalysisResult, BillingRecord, Upload
from app.services.dynamodb_service import DynamoDBService


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


def make_dynamo_service() -> DynamoDBService:
    client = FakeClient()
    return DynamoDBService(table_name="RevenueLeakage", client=client)


def test_upload_repository_item_structure_matches_example():
    dynamo = make_dynamo_service()
    repo = UploadRepository(dynamo)

    upload = Upload(
        upload_id="u_001",
        file_name="sample-billing.csv",
        file_type="csv",
        s3_key="uploads/u_001/sample-billing.csv",
        status="COMPLETED",
        uploaded_at=date(2026, 4, 1),
        record_count=12,
    )

    item = repo.create_upload_item(upload)
    assert item["pk"]["S"] == "UPLOAD#u_001"
    assert item["sk"]["S"] == "META"
    assert item["entity_type"]["S"] == "UPLOAD"
    assert item["file_name"]["S"] == "sample-billing.csv"
    assert item["record_count"]["N"] == "12"


def test_record_repository_item_structure_includes_gsis():
    dynamo = make_dynamo_service()
    repo = RecordRepository(dynamo)

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

    item = repo.create_billing_record_item(record)
    assert item["pk"]["S"] == "UPLOAD#u_001"
    assert item["sk"]["S"] == "RECORD#r_001"
    assert item["entity_type"]["S"] == "BILLING_RECORD"
    assert item["gsi1pk"]["S"] == "UPLOAD#u_001"
    assert "SEVERITY#" in item["gsi1sk"]["S"]
    assert item["gsi2pk"]["S"].startswith("FLAGGED#")
    assert item["gsi2sk"]["S"].startswith("UPLOAD#u_001#SEVERITY#")


def test_record_repository_update_summary_fields_calls_update():
    client = FakeClient()
    dynamo = DynamoDBService(table_name="RevenueLeakage", client=client)
    repo = RecordRepository(dynamo)

    repo.update_summary_fields(
        "u_001",
        "r_001",
        has_leakage=True,
        leakage_amount=80.0,
        severity=Severity.HIGH,
        issue_count=1,
        primary_issue_type=IssueType.RATE_MISMATCH,
        analysis_status="COMPLETED",
    )

    assert len(client.update_calls) == 1
    call = client.update_calls[0]
    assert call["Key"]["pk"]["S"] == "UPLOAD#u_001"
    assert "#severity" in call["ExpressionAttributeNames"]
    assert ":severity" in call["ExpressionAttributeValues"]


def test_analysis_repository_item_structure_matches_example():
    dynamo = make_dynamo_service()
    repo = AnalysisRepository(dynamo)

    issue = AnalysisIssue(
        id="r_001",
        issue=IssueType.RATE_MISMATCH.value,
        expected_amount=1000.0,
        billed_amount=920.0,
        leakage=80.0,
        reasoning="Billed rate is lower than the contract rate.",
        severity=Severity.HIGH.value,
        suggestion="Correct the billed rate and rebill the difference.",
    )
    result = AnalysisResult(
        record_id="r_001",
        issues=[issue],
        has_leakage=True,
        total_leakage_amount=80.0,
        analysis_status="COMPLETED",
        analyzer_type="RULE_PLUS_LLM",
        analysis_version=1,
    )

    item = repo.create_analysis_item("u_001", result)
    assert item["pk"]["S"] == "UPLOAD#u_001"
    assert item["sk"]["S"] == "ANALYSIS#r_001#v1"
    assert item["entity_type"]["S"] == "ANALYSIS_RESULT"
    assert item["record_id"]["S"] == "r_001"
    assert item["analysis_version"]["N"] == "1"
    stored_issue = item["issues"]["L"][0]
    assert stored_issue["id"] == "r_001"
    assert stored_issue["issue"] == IssueType.RATE_MISMATCH.value
    assert stored_issue["leakage"] == 80.0

