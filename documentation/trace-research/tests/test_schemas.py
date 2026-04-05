from trace_core.schemas import Claim, ClaimAssessment, ReliabilityReport


def test_unsupported_claim_count() -> None:
    report = ReliabilityReport(
        case_id="case-001",
        assessments=[
            ClaimAssessment(claim=Claim(claim_id="c1", text="Claim 1"), label="unsupported"),
            ClaimAssessment(claim=Claim(claim_id="c2", text="Claim 2"), label="inferred"),
        ],
    )

    assert report.unsupported_claim_count() == 1
