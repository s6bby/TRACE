"""Deterministic fallback evaluator for TRACE."""

from __future__ import annotations

from trace_backend.claims.models import Claim
from trace_backend.pipeline.models import EvidenceCandidate, JudgeDecision


def heuristic_judge_decision(claim: Claim, evidence: list[EvidenceCandidate]) -> JudgeDecision:
    """Return a deterministic fallback decision when no local LLM judges are configured."""

    if not evidence:
        return JudgeDecision(
            judge_id="heuristic",
            label="unsupported",
            cited_evidence_ids=[],
            rationale="No evidence candidates were retrieved for this claim.",
            ambiguity_note="",
            review_priority="high",
            metadata={"mode": "heuristic"},
        )

    top = evidence[0]
    exact_like = top.lexical_score >= 1.4
    has_semantic_support = top.semantic_score is not None and top.semantic_score >= 0.55

    if exact_like:
        label = "explicit"
        rationale = "The top evidence candidate has strong lexical overlap with the claim."
    elif has_semantic_support or top.lexical_score >= 0.45:
        label = "inferred"
        rationale = "The retrieved evidence appears relevant but does not justify a direct-support label deterministically."
    else:
        label = "unsupported"
        rationale = "Retrieved evidence is weak and does not justify support without further review."

    priority = "high" if claim.ambiguous or label == "unsupported" else "normal"
    return JudgeDecision(
        judge_id="heuristic",
        label=label,
        cited_evidence_ids=[top.evidence_id] if label != "unsupported" else [],
        rationale=rationale,
        ambiguity_note=", ".join(claim.ambiguity_reasons) if claim.ambiguous else "",
        review_priority=priority,
        metadata={"mode": "heuristic"},
    )
