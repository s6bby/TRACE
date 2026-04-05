"""TRACE claim extraction with deterministic validation and ambiguity tracking."""

from __future__ import annotations

import re

from trace_backend.claims.models import (
    Claim,
    ClaimExtractionConfig,
    ClaimExtractionMetrics,
    ClaimExtractionResult,
    ClaimFinding,
)
from trace_backend.claims.utils import (
    ENUMERATION_INTRODUCER_RE,
    contains_conditional_marker,
    contains_likely_verb,
    is_heading_like,
    iter_response_blocks,
    normalize_claim_text,
    normalize_whitespace,
    split_sentences,
    starts_with_referential_marker,
    suggest_connector_split,
    suggest_enumeration_splits,
    tokenize,
)
from trace_backend.claims.validation import validate_extracted_claims


def _classify_claim_type(text: str, block_kind: str) -> str:
    normalized = normalize_claim_text(text)
    lowered = normalized.lower()

    if block_kind == "list_item":
        return "list_item"
    if normalized.endswith("?"):
        return "question"
    if re.search(r"\b(?:should|recommend(?:s|ed)?|suggest(?:s|ed)?)\b", lowered):
        return "recommendation"
    if re.search(r"\b(?:must|shall|required|needs?\s+to|need\s+to)\b", lowered):
        return "obligation"
    return "statement"


def _has_compound_connector(text: str) -> bool:
    lowered = f" {normalize_claim_text(text).lower()} "
    for connector in (" but ", " however ", " whereas ", " although ", " while "):
        if connector in lowered:
            return True

    for connector in (" and ", " or "):
        if connector not in lowered:
            continue
        left, right = lowered.split(connector, 1)
        if contains_likely_verb(left) and contains_likely_verb(right):
            return True

    return False


def _has_enumeration_pattern(text: str) -> bool:
    normalized = normalize_claim_text(text)
    match = ENUMERATION_INTRODUCER_RE.match(normalized)
    if match is None:
        return False

    items_text = match.group("items")
    return "," in items_text or bool(re.search(r"\b(?:and|or)\b", items_text))


def _is_fragment_like(text: str, block_kind: str, config: ClaimExtractionConfig) -> bool:
    normalized = normalize_claim_text(text)
    if not normalized:
        return True

    if normalized.endswith((".", "!")) and len(tokenize(normalized)) >= config.min_claim_tokens:
        return False

    if block_kind != "list_item" and normalized.endswith(":"):
        return True

    tokens = tokenize(normalized)
    if len(tokens) < config.min_claim_tokens and not re.search(r"\d", normalized):
        return True

    if block_kind == "list_item":
        return False

    if contains_likely_verb(normalized):
        return False

    if ":" in normalized:
        label, value = normalized.split(":", 1)
        if label.strip() and value.strip():
            return False

    return len(tokens) < config.max_heading_tokens


def _dedupe_suggestions(suggestions: list[str], limit: int, claim_text: str) -> list[str]:
    deduped: list[str] = []
    normalized_claim = normalize_claim_text(claim_text).rstrip(".")

    for suggestion in suggestions:
        normalized_suggestion = normalize_claim_text(suggestion).rstrip(".")
        if not normalized_suggestion or normalized_suggestion == normalized_claim:
            continue
        if suggestion not in deduped:
            deduped.append(suggestion)
        if len(deduped) >= limit:
            break

    return deduped


class ClaimExtractor:
    """Extract evaluable claims from a raw model response."""

    def __init__(self, config: ClaimExtractionConfig | None = None) -> None:
        self.config = config or ClaimExtractionConfig()

    def extract(self, response_text: str) -> ClaimExtractionResult:
        findings: list[ClaimFinding] = []
        claims: list[Claim] = []

        skipped_heading_count = 0
        skipped_question_count = 0
        skipped_fragment_count = 0
        sentence_count = 0

        blocks = iter_response_blocks(response_text)

        for block_index, block in enumerate(blocks, start=1):
            block_text = normalize_claim_text(block.span.text)
            if not block_text:
                continue

            if (
                block.block_kind != "list_item"
                and is_heading_like(block_text, self.config)
                and not self.config.retain_headings_as_claims
            ):
                skipped_heading_count += 1
                findings.append(
                    ClaimFinding(
                        code="claim-heading-skipped",
                        severity="info",
                        message="A heading-like block was skipped because it is not an evaluable claim.",
                        span=block.span,
                        metadata={"block_index": block_index, "block_text": block_text},
                    )
                )
                continue

            candidate_spans = (
                split_sentences(block.span, self.config)
                if block.block_kind != "list_item"
                else [block.span]
            )

            for sentence_index, candidate_span in enumerate(candidate_spans, start=1):
                sentence_count += 1
                claim_text = normalize_claim_text(candidate_span.text)
                if not claim_text:
                    continue

                claim_type = _classify_claim_type(claim_text, block.block_kind)
                if claim_type == "question" and not self.config.treat_questions_as_claims:
                    skipped_question_count += 1
                    findings.append(
                        ClaimFinding(
                            code="claim-question-skipped",
                            severity="info",
                            message="A question-like response span was skipped because TRACE evaluates assertions, not prompts.",
                            span=candidate_span,
                            metadata={
                                "block_index": block_index,
                                "sentence_index": sentence_index,
                                "claim_text": claim_text,
                            },
                        )
                    )
                    continue

                if _is_fragment_like(claim_text, block.block_kind, self.config):
                    skipped_fragment_count += 1
                    findings.append(
                        ClaimFinding(
                            code="claim-fragment-skipped",
                            severity="info",
                            message="A short or non-assertive fragment was skipped during claim decomposition.",
                            span=candidate_span,
                            metadata={
                                "block_index": block_index,
                                "sentence_index": sentence_index,
                                "claim_text": claim_text,
                            },
                        )
                    )
                    continue

                ambiguity_reasons: list[str] = []
                suggested_split_claims: list[str] = []

                if self.config.detect_conditionals and contains_conditional_marker(claim_text):
                    ambiguity_reasons.append("conditional")

                if self.config.detect_referential_claims and starts_with_referential_marker(claim_text):
                    ambiguity_reasons.append("referential")

                if self.config.detect_compound_claims and _has_compound_connector(claim_text):
                    connector_splits = suggest_connector_split(claim_text)
                    if connector_splits:
                        ambiguity_reasons.append("contrast")
                        suggested_split_claims.extend(connector_splits)
                    else:
                        ambiguity_reasons.append("compound")

                if self.config.detect_enumerations and _has_enumeration_pattern(claim_text):
                    ambiguity_reasons.append("enumeration")
                    suggested_split_claims.extend(
                        suggest_enumeration_splits(
                            claim_text,
                            max_splits=self.config.max_suggested_splits,
                        )
                    )

                claim = Claim(
                    claim_id=f"claim-{len(claims) + 1}",
                    text=claim_text,
                    source_span=candidate_span,
                    response_span=candidate_span.text,
                    claim_type=claim_type,
                    ambiguous=bool(ambiguity_reasons),
                    ambiguity_reasons=ambiguity_reasons,
                    suggested_split_claims=_dedupe_suggestions(
                        suggested_split_claims,
                        limit=self.config.max_suggested_splits,
                        claim_text=claim_text,
                    ),
                    metadata={
                        "block_index": block_index,
                        "sentence_index": sentence_index,
                        "block_kind": block.block_kind,
                        "token_count": len(tokenize(claim_text)),
                    },
                )
                claims.append(claim)

                if claim.ambiguous:
                    findings.append(
                        ClaimFinding(
                            code="claim-boundary-ambiguous",
                            severity="warning",
                            message=(
                                "This claim may combine multiple ideas or depend on context. "
                                "It should receive extra review before downstream labeling."
                            ),
                            claim_id=claim.claim_id,
                            span=claim.source_span,
                            metadata={
                                "ambiguity_reasons": claim.ambiguity_reasons,
                                "suggested_split_claims": claim.suggested_split_claims,
                            },
                        )
                    )

        findings.extend(validate_extracted_claims(response_text, claims))

        return ClaimExtractionResult(
            response_text=response_text,
            claims=claims,
            findings=findings,
            metrics=ClaimExtractionMetrics(
                block_count=len(blocks),
                sentence_count=sentence_count,
                claim_count=len(claims),
                ambiguous_claim_count=sum(1 for claim in claims if claim.ambiguous),
                skipped_heading_count=skipped_heading_count,
                skipped_question_count=skipped_question_count,
                skipped_fragment_count=skipped_fragment_count,
            ),
            metadata={
                "method": "deterministic-heuristic",
                "scope_note": (
                    "TRACE uses conservative claim extraction and explicitly flags "
                    "boundary instability for later review."
                ),
            },
        )


def extract_claims(
    response_text: str,
    config: ClaimExtractionConfig | None = None,
) -> ClaimExtractionResult:
    """Convenience wrapper for TRACE claim extraction."""

    return ClaimExtractor(config=config).extract(response_text)
