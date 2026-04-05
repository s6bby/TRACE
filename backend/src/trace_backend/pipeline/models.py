"""Shared TRACE pipeline models for retrieval and evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from trace_backend.claims.models import Claim

SupportLabel = Literal["explicit", "inferred", "unsupported"]
ReviewPriority = Literal["low", "normal", "high"]
AgreementStatus = Literal["heuristic", "single_judge", "consensus", "adjudicated", "contested"]
Severity = Literal["info", "warning", "error"]


@dataclass(slots=True)
class EvidenceCandidate:
    """A retrieved evidence candidate for one claim."""

    evidence_id: str
    document_id: str
    source_path: Path
    snippet: str
    page_number: int | None
    section: str | None
    block_kind: str
    retrieval_rank: int
    fused_score: float
    lexical_score: float
    semantic_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievalFinding:
    """A retrieval-layer finding that may affect downstream reliability."""

    code: str
    severity: Severity
    message: str
    claim_id: str | None = None
    evidence_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class JudgeDecision:
    """A single judge model's provisional claim decision."""

    judge_id: str
    label: SupportLabel
    cited_evidence_ids: list[str]
    rationale: str
    ambiguity_note: str = ""
    review_priority: ReviewPriority = "normal"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationFinding:
    """A deterministic evaluation validation result."""

    code: str
    severity: Severity
    message: str
    claim_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ReportFinding:
    """A final report-level finding surfaced to the reviewer."""

    code: str
    severity: Severity
    message: str
    claim_id: str | None = None
    evidence_id: str | None = None
    document_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ReportSummary:
    """Aggregate metrics for one TRACE report."""

    total_claims: int
    explicit_count: int
    inferred_count: int
    unsupported_count: int
    ambiguous_claim_count: int
    high_priority_count: int
    contested_count: int
    evidence_backed_claim_count: int
    retrieval_warning_count: int
    validation_error_count: int
    evidence_coverage: float
    citation_validity_rate: float


@dataclass(slots=True)
class ClaimAssessment:
    """A TRACE assessment for one extracted claim."""

    claim: Claim
    label: SupportLabel
    evidence: list[EvidenceCandidate] = field(default_factory=list)
    cited_evidence_ids: list[str] = field(default_factory=list)
    note: str = ""
    review_priority: ReviewPriority = "normal"
    agreement_status: AgreementStatus = "heuristic"
    judge_decisions: list[JudgeDecision] = field(default_factory=list)
    validation_findings: list[ValidationFinding] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ReliabilityReport:
    """A structured reliability report across all extracted claims."""

    case_id: str
    assessments: list[ClaimAssessment]
    summary: ReportSummary | None = None
    findings: list[ReportFinding] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def unsupported_claim_count(self) -> int:
        """Return the number of unsupported claims in the report."""

        return sum(1 for assessment in self.assessments if assessment.label == "unsupported")
