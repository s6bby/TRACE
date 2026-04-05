"""Prompt construction for TRACE local judges."""

from __future__ import annotations

from trace_backend.claims.models import Claim
from trace_backend.pipeline.models import EvidenceCandidate, JudgeDecision


def build_claim_evaluation_messages(claim: Claim, evidence: list[EvidenceCandidate]) -> list[dict[str, str]]:
    """Build strict evaluation messages for one claim."""

    evidence_lines = []
    for item in evidence:
        evidence_lines.append(
            "\n".join(
                [
                    f"[{item.evidence_id}]",
                    f"document={item.document_id}",
                    f"page={item.page_number}",
                    f"section={item.section or 'unknown'}",
                    f"kind={item.block_kind}",
                    f"text={item.snippet}",
                ]
            )
        )

    ambiguity_note = (
        ", ".join(claim.ambiguity_reasons)
        if claim.ambiguity_reasons
        else "none"
    )
    suggested_splits = "; ".join(claim.suggested_split_claims) or "none"

    system_message = (
        "You are TRACE, a constrained claim-evaluation judge. "
        "Evaluate the claim only against the provided evidence. "
        "Do not use outside knowledge. "
        "Return one JSON object with keys: "
        "label, cited_evidence_ids, rationale, ambiguity_note, review_priority. "
        "label must be one of explicit, inferred, unsupported. "
        "cited_evidence_ids must only contain provided evidence ids. "
        "If the claim is unsupported, cited_evidence_ids should usually be empty."
    )

    user_message = "\n\n".join(
        [
            f"CLAIM:\n{claim.text}",
            f"CLAIM_TYPE:\n{claim.claim_type}",
            f"CLAIM_AMBIGUOUS:\n{str(claim.ambiguous).lower()}",
            f"CLAIM_AMBIGUITY_REASONS:\n{ambiguity_note}",
            f"SUGGESTED_SPLIT_CLAIMS:\n{suggested_splits}",
            "EVIDENCE_CANDIDATES:\n" + ("\n\n".join(evidence_lines) if evidence_lines else "none"),
            (
                'Return JSON only, for example: '
                '{"label":"inferred","cited_evidence_ids":["doc-1"],'
                '"rationale":"...","ambiguity_note":"","review_priority":"high"}'
            ),
        ]
    )

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]


def build_adjudication_messages(
    claim: Claim,
    evidence: list[EvidenceCandidate],
    prior_decisions: list[JudgeDecision],
) -> list[dict[str, str]]:
    """Build adjudication messages when judges disagree."""

    prior_lines = [
        "\n".join(
            [
                f"judge={decision.judge_id}",
                f"label={decision.label}",
                f"citations={', '.join(decision.cited_evidence_ids) or 'none'}",
                f"review_priority={decision.review_priority}",
                f"rationale={decision.rationale}",
            ]
        )
        for decision in prior_decisions
    ]

    base_messages = build_claim_evaluation_messages(claim, evidence)
    adjudicator_system = (
        base_messages[0]["content"]
        + " You are acting as an adjudicator because prior judges disagreed. "
        + "Resolve the disagreement using only the evidence list."
    )
    adjudicator_user = base_messages[1]["content"] + "\n\nPRIOR_JUDGE_OUTPUTS:\n" + "\n\n".join(prior_lines)

    return [
        {"role": "system", "content": adjudicator_system},
        {"role": "user", "content": adjudicator_user},
    ]
