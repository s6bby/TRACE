"""Configuration models for TRACE evaluation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class JudgeConfig:
    """Configuration for one local judge model."""

    judge_id: str
    base_url: str
    model: str
    api_key: str | None = None
    timeout_seconds: float = 60.0


@dataclass(slots=True)
class EvaluationConfig:
    """Configuration for multi-judge claim evaluation."""

    top_k_evidence: int = 5
    require_citations_for_supported_labels: bool = True
    validate_citation_membership: bool = True
    high_priority_on_ambiguity: bool = True
    high_priority_on_contested_label: bool = True
    allow_single_judge: bool = True
    conservative_resolution: bool = True
