from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from ..models.enums import IssueType, Severity
from ..schemas.common import BillingRecord
from ..services.dynamodb_service import DynamoDBService
from ..tools.severity_tool import assign_severity_from_leakage
from ..utils.money import compute_leakage_amount


class RecordRepository:
    def __init__(self, dynamo: DynamoDBService) -> None:
        self._dynamo = dynamo

    def create_billing_record_item(self, record: BillingRecord) -> Dict:
        if not record.upload_id or not record.record_id:
            raise ValueError("record.upload_id and record.record_id are required")

        created_at = datetime.now(timezone.utc).isoformat()
        leakage = (
            float(record.leakage_amount)
            if record.leakage_amount is not None
            else compute_leakage_amount(record.expected_amount, record.billed_amount)
        )
        has_leakage = record.has_leakage if record.has_leakage is not None else (leakage > 0)
        if record.severity:
            try:
                severity = Severity(record.severity)
            except ValueError:
                severity = assign_severity_from_leakage(leakage)
        else:
            severity = assign_severity_from_leakage(leakage)

        gsi1pk = f"UPLOAD#{record.upload_id}"
        leakage_str = f"{int(leakage):010d}"
        gsi1sk = f"SEVERITY#{severity.value}#LEAKAGE#{leakage_str}#RECORD#{record.record_id}"

        gsi2pk = f"FLAGGED#{'YES' if has_leakage else 'NO'}"
        gsi2sk = f"UPLOAD#{record.upload_id}#SEVERITY#{severity.value}#RECORD#{record.record_id}"

        item = {
            "pk": {"S": f"UPLOAD#{record.upload_id}"},
            "sk": {"S": f"RECORD#{record.record_id}"},
            "entity_type": {"S": "BILLING_RECORD"},
            "upload_id": {"S": record.upload_id},
            "record_id": {"S": record.record_id},
            "contract_id": {"S": record.contract_id or ""},
            "customer_id": {"S": record.customer_id or ""},
            "product_id": {"S": record.product_id or ""},
            "agreed_rate": {"N": str(record.agreed_rate or 0)},
            "billed_rate": {"N": str(record.billed_rate or 0)},
            "quantity": {"N": str(record.quantity or 0)},
            "expected_amount": {"N": str(record.expected_amount or 0)},
            "billed_amount": {"N": str(record.billed_amount or 0)},
            "discount": {"N": str(record.discount or 0)},
            "tax": {"N": str(record.tax or 0)},
            "currency": {"S": record.currency or ""},
            "billing_date": {"S": record.billing_date.isoformat() if record.billing_date else ""},
            "contract_start_date": {
                "S": record.contract_start_date.isoformat() if record.contract_start_date else ""
            },
            "contract_end_date": {"S": record.contract_end_date.isoformat() if record.contract_end_date else ""},
            "region": {"S": record.region or ""},
            "has_leakage": {"BOOL": has_leakage},
            "leakage_amount": {"N": str(leakage)},
            "severity": {"S": severity.value},
            "issue_count": {"N": "0"},
            "primary_issue_type": {"S": IssueType.RATE_MISMATCH.value if has_leakage else ""},
            "analysis_status": {"S": "PENDING"},
            "gsi1pk": {"S": gsi1pk},
            "gsi1sk": {"S": gsi1sk},
            "gsi2pk": {"S": gsi2pk},
            "gsi2sk": {"S": gsi2sk},
            "created_at": {"S": created_at},
        }
        self._dynamo.put(item)
        return item

    def update_summary_fields(
        self,
        upload_id: str,
        record_id: str,
        *,
        has_leakage: bool,
        leakage_amount: float,
        severity: Severity,
        issue_count: int,
        primary_issue_type: IssueType | None,
        analysis_status: str,
    ) -> None:
        key = {
            "pk": {"S": f"UPLOAD#{upload_id}"},
            "sk": {"S": f"RECORD#{record_id}"},
        }
        names = {
            "has_leakage": "has_leakage",
            "leakage_amount": "leakage_amount",
            "severity": "severity",
            "issue_count": "issue_count",
            "primary_issue_type": "primary_issue_type",
            "analysis_status": "analysis_status",
        }
        values = {
            "has_leakage": {"BOOL": has_leakage},
            "leakage_amount": {"N": str(leakage_amount)},
            "severity": {"S": severity.value},
            "issue_count": {"N": str(issue_count)},
            "primary_issue_type": {"S": primary_issue_type.value if primary_issue_type else ""},
            "analysis_status": {"S": analysis_status},
        }
        update_expr = (
            "SET #has_leakage = :has_leakage, "
            "#leakage_amount = :leakage_amount, "
            "#severity = :severity, "
            "#issue_count = :issue_count, "
            "#primary_issue_type = :primary_issue_type, "
            "#analysis_status = :analysis_status"
        )
        self._dynamo.update(key=key, update_expression=update_expr, names=names, values=values)

