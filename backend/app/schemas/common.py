from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class MoneyAmount(BaseModel):
    currency: str = Field(..., min_length=1)
    amount: float


class Upload(BaseModel):
    upload_id: str
    file_name: str
    file_type: str
    s3_key: Optional[str] = None
    status: str
    uploaded_at: date
    record_count: Optional[int] = None


class BillingRecord(BaseModel):
    upload_id: Optional[str] = None
    record_id: Optional[str] = None

    contract_id: Optional[str] = None
    customer_id: Optional[str] = None
    product_id: Optional[str] = None

    agreed_rate: Optional[float] = None
    billed_rate: Optional[float] = None
    quantity: Optional[float] = None

    expected_amount: Optional[float] = None
    billed_amount: Optional[float] = None

    discount: Optional[float] = None
    tax: Optional[float] = None

    currency: Optional[str] = None
    billing_date: Optional[date] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    region: Optional[str] = None
    tier_pricing: Optional[dict] = None
    manual_override: Optional[bool] = None

    # Optional analysis summary fields for fast dashboard rendering
    has_leakage: Optional[bool] = None
    leakage_amount: Optional[float] = None
    severity: Optional[str] = None


class AnalysisIssue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    issue: str = Field(..., validation_alias="issue_type")
    expected_amount: Optional[float] = None
    billed_amount: Optional[float] = None
    leakage: Optional[float] = Field(default=None, validation_alias="leakage_amount")
    reasoning: str = Field(..., validation_alias="message")
    severity: str
    suggestion: Optional[str] = None
    confidence_score: Optional[float] = None

    @property
    def issue_type(self) -> str:
        return self.issue

    @property
    def message(self) -> str:
        return self.reasoning

    @property
    def leakage_amount(self) -> Optional[float]:
        return self.leakage


class AnalysisResult(BaseModel):
    record_id: str
    issues: list[AnalysisIssue]
    has_leakage: bool
    total_leakage_amount: float
    analysis_status: str
    analyzer_type: str
    analysis_version: int = 1


class DashboardSummary(BaseModel):
    total_records: int
    flagged_records: int
    total_leakage_amount: float
    high_severity_count: int
    data_source: Literal["dynamodb", "memory"] = "memory"

