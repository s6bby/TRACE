"""Deterministic validation for final TRACE reliability reports."""

from __future__ import annotations

from trace_backend.pipeline.models import (
    ClaimAssessment,
    ReportFinding,
    ReportSummary,
    ReliabilityReport,
)
from trace_backend.retrieval.utils import normalize_text
from trace_backend.scanning.models import DocumentScanResult


def _document_lookup(documents: list[DocumentScanResult]) -> dict[str, DocumentScanResult]:
    return {document.source_path.stem: document for document in documents}


def _evidence_snippet_exists(snippet: str, document: DocumentScanResult) -> bool:
    normalized_snippet = normalize_text(snippet)
    normalized_text = normalize_text(document.text)
    return bool(normalized_snippet and normalized_snippet in normalized_text)


def validate_assessment_against_sources(
    assessment: ClaimAssessment,
    documents: list[DocumentScanResult],
) -> list[ReportFinding]:
    """Validate one assessment against the source corpus and TRACE rules."""

    findings: list[ReportFinding] = []
    document_lookup = _document_lookup(documents)
    claim_id = assessment.claim.claim_id

    retrieval_findings = assessment.metadata.get("retrieval_findings", [])
    for retrieval_finding in retrieval_findings:
        findings.append(
            ReportFinding(
                code=retrieval_finding.code,
                severity=retrieval_finding.severity,
                message=retrieval_finding.message,
                claim_id=claim_id,
                evidence_id=retrieval_finding.evidence_id,
                metadata=retrieval_finding.metadata,
            )
        )

    for validation_finding in assessment.validation_findings:
        findings.append(
            ReportFinding(
                code=validation_finding.code,
                severity=validation_finding.severity,
                message=validation_finding.message,
                claim_id=claim_id,
                metadata=validation_finding.metadata,
            )
        )

    if assessment.label in {"explicit", "inferred"} and not assessment.cited_evidence_ids:
        findings.append(
            ReportFinding(
                code="report-missing-citations",
                severity="error",
                message="A supported claim is missing cited evidence ids in the final report.",
                claim_id=claim_id,
            )
        )

    if assessment.label == "unsupported" and assessment.cited_evidence_ids:
        findings.append(
            ReportFinding(
                code="report-unsupported-citations-present",
                severity="warning",
                message="An unsupported claim still carries citations in the final report.",
                claim_id=claim_id,
                metadata={"cited_evidence_ids": assessment.cited_evidence_ids},
            )
        )

    if assessment.agreement_status in {"heuristic", "single_judge"}:
        findings.append(
            ReportFinding(
                code="report-limited-judge-redundancy",
                severity="info",
                message="This claim was not reviewed by a full multi-judge panel.",
                claim_id=claim_id,
                metadata={"agreement_status": assessment.agreement_status},
            )
        )

    if assessment.agreement_status == "contested":
        findings.append(
            ReportFinding(
                code="report-contested-claim",
                severity="warning",
                message="Judge disagreement remained unresolved and the claim was elevated for review.",
                claim_id=claim_id,
            )
        )

    if assessment.claim.ambiguous:
        findings.append(
            ReportFinding(
                code="report-ambiguous-claim",
                severity="warning",
                message="The extracted claim boundary was ambiguous and should be reviewed manually.",
                claim_id=claim_id,
                metadata={"ambiguity_reasons": assessment.claim.ambiguity_reasons},
            )
        )

    for evidence in assessment.evidence:
        document = document_lookup.get(evidence.document_id)
        if document is None:
            findings.append(
                ReportFinding(
                    code="report-evidence-document-missing",
                    severity="error",
                    message="The cited evidence points to a document that was not present in the analysis set.",
                    claim_id=claim_id,
                    evidence_id=evidence.evidence_id,
                    document_id=evidence.document_id,
                )
            )
            continue

        if not _evidence_snippet_exists(evidence.snippet, document):
            findings.append(
                ReportFinding(
                    code="report-evidence-snippet-not-found",
                    severity="error",
                    message="The cited evidence snippet could not be re-matched to the scanned source text.",
                    claim_id=claim_id,
                    evidence_id=evidence.evidence_id,
                    document_id=evidence.document_id,
                )
            )

        if evidence.fused_score < 0.003:
            findings.append(
                ReportFinding(
                    code="report-weak-evidence-score",
                    severity="warning",
                    message="The cited evidence was retrieved with a weak fused retrieval score.",
                    claim_id=claim_id,
                    evidence_id=evidence.evidence_id,
                    document_id=evidence.document_id,
                    metadata={"fused_score": evidence.fused_score},
                )
            )

    return findings


def build_report_summary(report: ReliabilityReport) -> ReportSummary:
    """Compute summary metrics for a reliability report."""

    total_claims = len(report.assessments)
    explicit_count = sum(1 for assessment in report.assessments if assessment.label == "explicit")
    inferred_count = sum(1 for assessment in report.assessments if assessment.label == "inferred")
    unsupported_count = sum(1 for assessment in report.assessments if assessment.label == "unsupported")
    ambiguous_claim_count = sum(1 for assessment in report.assessments if assessment.claim.ambiguous)
    high_priority_count = sum(1 for assessment in report.assessments if assessment.review_priority == "high")
    contested_count = sum(1 for assessment in report.assessments if assessment.agreement_status == "contested")
    evidence_backed_claim_count = sum(1 for assessment in report.assessments if assessment.cited_evidence_ids)
    retrieval_warning_count = sum(1 for finding in report.findings if finding.code.startswith("retrieval-"))
    validation_error_count = sum(1 for finding in report.findings if finding.severity == "error")

    evidence_coverage = (
        evidence_backed_claim_count / total_claims
        if total_claims
        else 0.0
    )

    citation_checks = [
        finding
        for finding in report.findings
        if finding.code in {
            "report-missing-citations",
            "report-evidence-document-missing",
            "report-evidence-snippet-not-found",
            "evaluation-invalid-citation",
            "evaluation-citations-required",
        }
    ]
    citation_validity_rate = (
        (total_claims - len({finding.claim_id for finding in citation_checks if finding.claim_id}))
        / total_claims
        if total_claims
        else 0.0
    )

    return ReportSummary(
        total_claims=total_claims,
        explicit_count=explicit_count,
        inferred_count=inferred_count,
        unsupported_count=unsupported_count,
        ambiguous_claim_count=ambiguous_claim_count,
        high_priority_count=high_priority_count,
        contested_count=contested_count,
        evidence_backed_claim_count=evidence_backed_claim_count,
        retrieval_warning_count=retrieval_warning_count,
        validation_error_count=validation_error_count,
        evidence_coverage=evidence_coverage,
        citation_validity_rate=citation_validity_rate,
    )
