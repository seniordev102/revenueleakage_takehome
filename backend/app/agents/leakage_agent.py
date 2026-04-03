from __future__ import annotations

from typing import List, Tuple

from ..models.enums import IssueType, Severity
from ..repositories.analysis_repository import AnalysisRepository
from ..repositories.record_repository import RecordRepository
from ..schemas.common import AnalysisIssue, AnalysisResult, BillingRecord
from ..tools.contract_tool import run_contract_checks
from ..tools.discount_tool import run_discount_checks
from ..tools.duplicate_tool import run_duplicate_checks
from ..tools.incident_factory import build_incident
from ..tools.llm_reasoning_tool import LLMReasoningTool
from ..tools.manual_override_tool import run_manual_override_checks
from ..tools.pricing_tool import run_pricing_checks
from ..tools.quantity_tool import run_quantity_checks
from ..tools.severity_tool import assign_severity_from_leakage
from ..tools.tax_tool import run_tax_checks
from ..tools.validation_tool import run_validation_checks
from ..utils.money import compute_leakage_amount


class LeakageAnalysisAgent:
    """
    Orchestrates deterministic tools and optional LLM reasoning for a single billing record.
    """

    def __init__(
        self,
        record_repo: RecordRepository | None,
        analysis_repo: AnalysisRepository | None,
        llm_tool: LLMReasoningTool | None = None,
    ) -> None:
        self._record_repo = record_repo
        self._analysis_repo = analysis_repo
        self._llm_tool = llm_tool or LLMReasoningTool()

    def analyze_record(self, upload_id: str, record: BillingRecord) -> AnalysisResult:
        # 1–3: run deterministic tools and aggregate issues
        issues, total_leakage = self._run_all_tools(record)
        has_leakage = total_leakage > 0

        # 4–5: compute leakage/assign top severity at record level
        severity = assign_severity_from_leakage(total_leakage)

        # 6: decide whether LLM invocation is necessary
        result = AnalysisResult(
            record_id=record.record_id or "",
            issues=issues,
            has_leakage=has_leakage,
            total_leakage_amount=total_leakage,
            analysis_status="COMPLETED",
            analyzer_type="RULE_ONLY",
            analysis_version=1,
        )

        if self._llm_tool.should_call_llm(result):
            llm_payload = self._llm_tool.call_llm(record, result)
            result.issues = self._merge_llm_issue_details(result.issues, llm_payload.get("issues", []))
            result.analyzer_type = llm_payload.get("analyzer_type", "RULE_PLUS_LLM")

        # 7–9: persist analysis and update summary fields on billing record
        if self._analysis_repo is not None:
            self._analysis_repo.create_analysis_item(upload_id, result)
        primary_issue_type = self._derive_primary_issue_type(issues)
        if self._record_repo is not None:
            self._record_repo.update_summary_fields(
                upload_id,
                record.record_id or "",
                has_leakage=has_leakage,
                leakage_amount=total_leakage,
                severity=severity,
                issue_count=len(issues),
                primary_issue_type=primary_issue_type,
                analysis_status=result.analysis_status,
            )

        return result

    def _run_all_tools(self, record: BillingRecord) -> Tuple[List[AnalysisIssue], float]:
        issues: List[AnalysisIssue] = []

        issues.extend(run_validation_checks(record))
        issues.extend(run_pricing_checks(record))
        issues.extend(run_quantity_checks(record))
        issues.extend(run_discount_checks(record))
        issues.extend(run_tax_checks(record))
        issues.extend(run_contract_checks(record))
        issues.extend(run_manual_override_checks(record))
        # duplicate checks are better run at batch level; for now we skip here

        total_leakage = 0.0
        for issue in issues:
            if issue.leakage_amount is not None:
                total_leakage += float(issue.leakage_amount)

        # fallback: if no issues provided leakage but record has expected/billed,
        # compute a simple leakage measure.
        if total_leakage == 0.0:
            total_leakage = compute_leakage_amount(record.expected_amount, record.billed_amount)

        if total_leakage > 0 and not issues:
            issues.append(
                build_incident(
                    record,
                    issue=IssueType.EXPECTED_VS_BILLED_DIFFERENCE,
                    severity=Severity.MEDIUM,
                    reasoning="Billed amount is lower than expected for this record.",
                    leakage=total_leakage,
                    suggestion="Review the invoice against the contract calculation and bill the missing amount.",
                )
            )

        issues = self._prioritize_issues(issues)
        return issues, total_leakage

    @staticmethod
    def _prioritize_issues(issues: List[AnalysisIssue]) -> List[AnalysisIssue]:
        severity_rank = {Severity.HIGH: 3, Severity.MEDIUM: 2, Severity.LOW: 1, Severity.INFO: 0}
        return sorted(
            issues,
            key=lambda issue: (
                severity_rank.get(issue.severity, 0),
                issue.leakage or 0,
            ),
            reverse=True,
        )

    def _merge_llm_issue_details(
        self, issues: List[AnalysisIssue], llm_issues: List[dict]
    ) -> List[AnalysisIssue]:
        if not llm_issues:
            return issues

        merged: List[AnalysisIssue] = []
        remaining = list(llm_issues)

        for issue in issues:
            match_index = next(
                (
                    index
                    for index, candidate in enumerate(remaining)
                    if candidate.get("issue") == issue.issue
                    or candidate.get("issue_type") == issue.issue
                ),
                None,
            )
            if match_index is None:
                merged.append(issue)
                continue

            candidate = remaining.pop(match_index)
            merged.append(
                issue.model_copy(
                    update={
                        "reasoning": candidate.get("reasoning", issue.reasoning),
                        "suggestion": candidate.get("suggestion", issue.suggestion),
                        "confidence_score": candidate.get("confidence_score", issue.confidence_score),
                    }
                )
            )

        merged.extend(
            AnalysisIssue.model_validate(candidate)
            for candidate in remaining
            if isinstance(candidate, dict)
        )
        return self._prioritize_issues(merged)

    @staticmethod
    def _derive_primary_issue_type(issues: List[AnalysisIssue]) -> IssueType | None:
        if not issues:
            return None
        # Prefer highest severity, first occurrence
        severity_rank = {Severity.HIGH: 3, Severity.MEDIUM: 2, Severity.LOW: 1, Severity.INFO: 0}
        best_issue = max(issues, key=lambda i: severity_rank.get(i.severity, 0))
        try:
            return IssueType(best_issue.issue_type)
        except ValueError:
            return None

