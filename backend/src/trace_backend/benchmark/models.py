"""Benchmark models for TRACE evaluation runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class GoldClaim:
    """Gold annotation for one benchmark claim."""

    text: str
    label: str
    evidence_substrings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BenchmarkCase:
    """One benchmark case package."""

    case_id: str
    documents: list[Path]
    response_path: Path
    gold_claims: list[GoldClaim]


@dataclass(slots=True)
class BenchmarkCaseResult:
    """Measured metrics for one benchmark case."""

    case_id: str
    gold_claim_count: int
    predicted_claim_count: int
    matched_claim_count: int
    claim_precision: float
    claim_recall: float
    label_accuracy: float
    retrieval_recall_at_k: float
    citation_validity_rate: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BenchmarkSummary:
    """Aggregate benchmark metrics across all cases."""

    case_count: int
    total_gold_claims: int
    total_predicted_claims: int
    total_matched_claims: int
    claim_precision: float
    claim_recall: float
    label_accuracy: float
    retrieval_recall_at_k: float
    citation_validity_rate: float


@dataclass(slots=True)
class BenchmarkResult:
    """Full benchmark output."""

    dataset_path: Path
    cases: list[BenchmarkCaseResult]
    summary: BenchmarkSummary
