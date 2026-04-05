"""Shared data models for the TRACE pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SupportLabel = Literal["explicit", "inferred", "unsupported"]


@dataclass(slots=True)
class SourceDocument:
    """A source document used for evidence-grounded analysis."""

    document_id: str
    title: str
    text: str
    section: str | None = None


@dataclass(slots=True)
class Claim:
    """A unit of meaning extracted from a model response."""

    claim_id: str
    text: str
    response_span: str | None = None
    ambiguous: bool = False


@dataclass(slots=True)
class EvidenceSpan:
    """A candidate evidence span retrieved from the source documents."""

    document_id: str
    snippet: str
    section: str | None = None
    score: float | None = None


@dataclass(slots=True)
class ClaimAssessment:
    """A support judgment for a single claim."""

    claim: Claim
    label: SupportLabel
    evidence: list[EvidenceSpan] = field(default_factory=list)
    note: str = ""
    review_priority: str = "normal"


@dataclass(slots=True)
class ReliabilityReport:
    """A structured report produced by the TRACE pipeline."""

    case_id: str
    assessments: list[ClaimAssessment]

    def unsupported_claim_count(self) -> int:
        """Return the number of unsupported claims in the report."""
        return sum(1 for assessment in self.assessments if assessment.label == "unsupported")
