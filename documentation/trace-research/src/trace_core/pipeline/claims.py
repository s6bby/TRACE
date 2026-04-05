"""Claim extraction stage."""

from __future__ import annotations

from trace_core.schemas import Claim


def extract_claims(response_text: str) -> list[Claim]:
    """Extract claims from a model response.

    This placeholder implementation returns one claim per non-empty line.
    It exists to establish the module boundary for later replacement with
    a stricter schema-driven extraction step.
    """
    claims: list[Claim] = []

    for index, line in enumerate(response_text.splitlines(), start=1):
        text = line.strip()
        if not text:
            continue
        claims.append(Claim(claim_id=f"claim-{index}", text=text, response_span=text))

    return claims
