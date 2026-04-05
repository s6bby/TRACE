"""Deterministic validation for TRACE claim extraction."""

from __future__ import annotations

from trace_backend.claims.models import Claim, ClaimFinding, TextSpan
from trace_backend.claims.utils import normalize_claim_text


def validate_extracted_claims(response_text: str, claims: list[Claim]) -> list[ClaimFinding]:
    """Return structural findings for extracted claims."""

    findings: list[ClaimFinding] = []
    seen_ids: set[str] = set()
    previous_end = -1

    for claim in claims:
        if claim.claim_id in seen_ids:
            findings.append(
                ClaimFinding(
                    code="claim-id-duplicate",
                    severity="error",
                    message="Claim identifiers must be unique.",
                    claim_id=claim.claim_id,
                    span=claim.source_span,
                )
            )
        seen_ids.add(claim.claim_id)

        span = claim.source_span
        if span.start_char < 0 or span.end_char > len(response_text) or span.start_char >= span.end_char:
            findings.append(
                ClaimFinding(
                    code="claim-span-invalid",
                    severity="error",
                    message="Claim source span is outside the response text bounds.",
                    claim_id=claim.claim_id,
                    span=span,
                )
            )
            continue

        raw_text = response_text[span.start_char:span.end_char]
        if raw_text != span.text:
            findings.append(
                ClaimFinding(
                    code="claim-span-mismatch",
                    severity="error",
                    message="Claim source span text does not match the original response substring.",
                    claim_id=claim.claim_id,
                    span=span,
                )
            )

        if span.start_char < previous_end:
            findings.append(
                ClaimFinding(
                    code="claim-span-overlap",
                    severity="warning",
                    message="Claim spans are out of order or overlapping.",
                    claim_id=claim.claim_id,
                    span=span,
                )
            )
        previous_end = max(previous_end, span.end_char)

        if not normalize_claim_text(claim.text):
            findings.append(
                ClaimFinding(
                    code="claim-text-empty",
                    severity="error",
                    message="Claim text is empty after normalization.",
                    claim_id=claim.claim_id,
                    span=span,
                )
            )

        if claim.response_span is None:
            findings.append(
                ClaimFinding(
                    code="claim-response-span-missing",
                    severity="warning",
                    message="The claim is missing its response-span text link.",
                    claim_id=claim.claim_id,
                    span=span,
                )
            )

        deduped_suggestions: list[str] = []
        for suggestion in claim.suggested_split_claims:
            if suggestion not in deduped_suggestions:
                deduped_suggestions.append(suggestion)

        if len(deduped_suggestions) != len(claim.suggested_split_claims):
            claim.suggested_split_claims[:] = deduped_suggestions
            findings.append(
                ClaimFinding(
                    code="claim-suggestions-deduped",
                    severity="info",
                    message="Duplicate suggested split claims were removed during validation.",
                    claim_id=claim.claim_id,
                    span=span,
                    metadata={"suggestion_count": len(deduped_suggestions)},
                )
            )

    return findings
