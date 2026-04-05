"""Claim evaluation stage."""

from __future__ import annotations

from trace_core.schemas import Claim, ClaimAssessment, EvidenceSpan


def assess_claim(claim: Claim, evidence: list[EvidenceSpan]) -> ClaimAssessment:
    """Return a placeholder support judgment for a claim.

    Until a constrained evaluator is implemented, claims with at least one
    evidence candidate are marked as `inferred`; claims without evidence are
    marked as `unsupported`.
    """
    if evidence:
        return ClaimAssessment(
            claim=claim,
            label="inferred",
            evidence=evidence,
            note="Placeholder evaluation pending constrained support labeling.",
            review_priority="normal",
        )

    return ClaimAssessment(
        claim=claim,
        label="unsupported",
        evidence=[],
        note="No evidence candidates were returned.",
        review_priority="high",
    )
