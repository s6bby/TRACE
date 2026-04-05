"""Structured models for TRACE claim extraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Severity = Literal["info", "warning", "error"]
ClaimType = Literal["statement", "list_item", "recommendation", "obligation", "question", "fragment"]


@dataclass(slots=True)
class TextSpan:
    """A span of text in the original model response."""

    start_char: int
    end_char: int
    text: str


@dataclass(slots=True)
class Claim:
    """A unit of meaning extracted from a model response."""

    claim_id: str
    text: str
    source_span: TextSpan
    response_span: str | None = None
    claim_type: ClaimType = "statement"
    ambiguous: bool = False
    ambiguity_reasons: list[str] = field(default_factory=list)
    suggested_split_claims: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ClaimFinding:
    """A deterministic extraction or validation finding."""

    code: str
    severity: Severity
    message: str
    claim_id: str | None = None
    span: TextSpan | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ClaimExtractionMetrics:
    """Summary metrics for one claim extraction run."""

    block_count: int
    sentence_count: int
    claim_count: int
    ambiguous_claim_count: int
    skipped_heading_count: int
    skipped_question_count: int
    skipped_fragment_count: int


@dataclass(slots=True)
class ClaimExtractionResult:
    """Structured output from TRACE claim decomposition."""

    response_text: str
    claims: list[Claim]
    findings: list[ClaimFinding]
    metrics: ClaimExtractionMetrics
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ClaimExtractionConfig:
    """Configuration for the TRACE claim extractor."""

    min_claim_tokens: int = 2
    max_heading_tokens: int = 12
    split_on_semicolons: bool = True
    treat_questions_as_claims: bool = False
    retain_headings_as_claims: bool = False
    detect_conditionals: bool = True
    detect_referential_claims: bool = True
    detect_compound_claims: bool = True
    detect_enumerations: bool = True
    max_suggested_splits: int = 6
