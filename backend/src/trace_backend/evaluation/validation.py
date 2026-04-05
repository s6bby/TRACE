"""Deterministic validation for TRACE evaluator outputs."""

from __future__ import annotations

from trace_backend.claims.models import Claim
from trace_backend.pipeline.models import EvidenceCandidate, JudgeDecision, ValidationFinding


def validate_judge_decision(
    claim: Claim,
    decision: JudgeDecision,
    evidence: list[EvidenceCandidate],
) -> list[ValidationFinding]:
    """Validate a judge decision against TRACE rules."""

    findings: list[ValidationFinding] = []
    valid_ids = {item.evidence_id for item in evidence}

    if decision.label in {"explicit", "inferred"} and not decision.cited_evidence_ids:
        findings.append(
            ValidationFinding(
                code="evaluation-citations-required",
                severity="error",
                message="Non-unsupported labels must cite at least one evidence candidate.",
                claim_id=claim.claim_id,
                metadata={"judge_id": decision.judge_id, "label": decision.label},
            )
        )

    invalid_ids = [
        evidence_id
        for evidence_id in decision.cited_evidence_ids
        if evidence_id not in valid_ids
    ]
    if invalid_ids:
        findings.append(
            ValidationFinding(
                code="evaluation-invalid-citation",
                severity="error",
                message="The judge cited evidence ids that do not exist in the retrieval set.",
                claim_id=claim.claim_id,
                metadata={"judge_id": decision.judge_id, "invalid_ids": invalid_ids},
            )
        )

    if decision.label == "unsupported" and decision.cited_evidence_ids:
        findings.append(
            ValidationFinding(
                code="evaluation-unsupported-has-citations",
                severity="warning",
                message="An unsupported label still cited evidence. Review the rationale for inconsistency.",
                claim_id=claim.claim_id,
                metadata={"judge_id": decision.judge_id, "cited_ids": decision.cited_evidence_ids},
            )
        )

    if claim.ambiguous:
        findings.append(
            ValidationFinding(
                code="evaluation-ambiguous-claim",
                severity="warning",
                message="This claim was marked ambiguous during extraction and should receive elevated review.",
                claim_id=claim.claim_id,
                metadata={"judge_id": decision.judge_id, "ambiguity_reasons": claim.ambiguity_reasons},
            )
        )

    return findings
