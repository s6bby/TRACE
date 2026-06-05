from pathlib import Path

from surca_research_pipeline.src.claims.claim_extractor import (
    build_claim_breakdown,
    classify_claim_type,
    extract_claims,
    looks_like_claim,
    split_candidate_units,
)


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_split_candidate_units_breaks_response_into_sentences():
    units = split_candidate_units(read_fixture("response_broad_summary.txt"))

    assert len(units) >= 4
    assert units[0] == "The student shows aggression, yelling, and occasional task refusal during difficult work."
    assert any("The BIP is in place." in unit for unit in units)


def test_extract_claims_keeps_checkable_units():
    claims = extract_claims(read_fixture("response_broad_summary.txt"), prefix="broad")

    texts = [claim["source_text"] for claim in claims]
    types = [claim["claim_type"] for claim in claims]

    assert any("The BIP is in place." == text for text in texts)
    assert any("OT services are provided." == text for text in texts)
    assert "behavior" in types
    assert "service" in types
    assert "function" in types


def test_extract_claims_keeps_abstention_style_staffing_claims():
    claims = extract_claims(read_fixture("response_ratio_abstain.txt"), prefix="ratio")

    assert len(claims) == 2
    assert claims[0]["claim_type"] == "staffing_or_support"
    assert looks_like_claim(claims[1]["source_text"]) is True


def test_build_claim_breakdown_keeps_units_and_claim_counts():
    breakdown = build_claim_breakdown(read_fixture("response_broad_summary.txt"), prefix="broad")

    assert breakdown["source_unit_count"] >= breakdown["claim_count"]
    assert breakdown["claim_count"] >= 5
    assert any(unit["looks_like_claim"] is True for unit in breakdown["units"])
    assert breakdown["claims_by_type"]["behavior"] >= 1
    assert breakdown["claims_by_type"]["service"] >= 1
    assert any(claim["claim_id"] == "broad_001" for claim in breakdown["claims"])


def test_classify_claim_type_prefers_simple_domain_types():
    assert classify_claim_type("The student receives OT services.") == "service"
    assert classify_claim_type("The behavior appears to be maintained by escape.") == "function"
    assert classify_claim_type("A break card is available in class.") == "accommodation"
