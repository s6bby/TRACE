from __future__ import annotations

from trace_backend.claims import extract_claims


def test_extract_claims_splits_sentences_and_preserves_source_spans() -> None:
    response = (
        "Student Summary\n\n"
        "The student receives reading intervention. The student benefits from small-group instruction."
    )

    result = extract_claims(response)

    assert result.metrics.claim_count == 2
    assert result.metrics.skipped_heading_count == 1
    assert result.claims[0].text == "The student receives reading intervention."
    assert result.claims[1].text == "The student benefits from small-group instruction."
    for claim in result.claims:
        assert response[claim.source_span.start_char : claim.source_span.end_char] == claim.source_span.text


def test_extract_claims_skips_questions() -> None:
    response = "What services are provided?\n\nThe student receives speech therapy."

    result = extract_claims(response)

    assert result.metrics.claim_count == 1
    assert result.metrics.skipped_question_count == 1
    assert result.claims[0].text == "The student receives speech therapy."
    assert any(finding.code == "claim-question-skipped" for finding in result.findings)


def test_extract_claims_flags_contrastive_compound_statements() -> None:
    response = "The student struggles with reading, but math performance is improving."

    result = extract_claims(response)

    assert result.metrics.claim_count == 1
    assert result.metrics.ambiguous_claim_count == 1
    claim = result.claims[0]
    assert claim.ambiguous is True
    assert "contrast" in claim.ambiguity_reasons
    assert claim.suggested_split_claims == [
        "The student struggles with reading.",
        "Math performance is improving.",
    ]


def test_extract_claims_suggests_enumeration_subclaims() -> None:
    response = "The plan includes visual supports, extended time, and weekly check-ins."

    result = extract_claims(response)

    assert result.metrics.claim_count == 1
    claim = result.claims[0]
    assert "enumeration" in claim.ambiguity_reasons
    assert claim.suggested_split_claims == [
        "The plan includes visual supports.",
        "The plan includes extended time.",
        "The plan includes weekly check-ins.",
    ]


def test_extract_claims_keeps_list_items_and_flags_context_dependent_claims() -> None:
    response = (
        "- Speech therapy: 30 minutes weekly\n"
        "- This should continue when frustration increases.\n"
    )

    result = extract_claims(response)

    assert result.metrics.claim_count == 2
    assert all(claim.claim_type == "list_item" for claim in result.claims)
    assert result.claims[0].text == "Speech therapy: 30 minutes weekly"
    assert result.claims[1].ambiguous is True
    assert "referential" in result.claims[1].ambiguity_reasons
    assert "conditional" in result.claims[1].ambiguity_reasons
