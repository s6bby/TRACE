"""Minimal orchestration layer for the TRACE pipeline."""

from __future__ import annotations

from trace_core.pipeline.claims import extract_claims
from trace_core.pipeline.evaluation import assess_claim
from trace_core.pipeline.reporting import build_report
from trace_core.pipeline.retrieval import retrieve_evidence
from trace_core.schemas import ReliabilityReport, SourceDocument


class TracePipeline:
    """Coordinate the high-level TRACE workflow."""

    def run(self, case_id: str, response_text: str, documents: list[SourceDocument]) -> ReliabilityReport:
        """Run the placeholder pipeline on a model response."""
        claims = extract_claims(response_text)
        assessments = []

        for claim in claims:
            evidence = retrieve_evidence(claim, documents)
            assessments.append(assess_claim(claim, evidence))

        return build_report(case_id=case_id, assessments=assessments)
