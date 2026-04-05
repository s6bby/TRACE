"""Final report building for TRACE."""

from __future__ import annotations

from datetime import datetime, timezone

from trace_backend.claims.models import ClaimExtractionResult
from trace_backend.pipeline.models import ClaimAssessment, ReliabilityReport
from trace_backend.pipeline.validation import build_report_summary, validate_assessment_against_sources
from trace_backend.scanning.models import DocumentScanResult


def build_reliability_report(
    case_id: str,
    documents: list[DocumentScanResult],
    claim_result: ClaimExtractionResult,
    assessments: list[ClaimAssessment],
) -> ReliabilityReport:
    """Assemble the final TRACE reliability report."""

    findings = []
    for assessment in assessments:
        findings.extend(validate_assessment_against_sources(assessment, documents))

    report = ReliabilityReport(
        case_id=case_id,
        assessments=assessments,
        findings=findings,
        metadata={
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "claim_extraction_metrics": claim_result.metrics,
            "claim_extraction_findings": claim_result.findings,
            "document_count": len(documents),
            "source_documents": [
                {
                    "document_id": document.source_path.stem,
                    "source_path": document.source_path,
                    "file_kind": document.file_kind,
                    "page_count": document.metrics.page_count,
                    "finding_count": len(document.findings),
                }
                for document in documents
            ],
        },
    )
    report.summary = build_report_summary(report)
    return report
