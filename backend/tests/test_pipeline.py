from __future__ import annotations

from pathlib import Path

from trace_backend.pipeline.orchestrator import TraceAnalysisPipeline
from trace_backend.scanning import DocumentScanner


def test_trace_analysis_pipeline_runs_end_to_end(tmp_path: Path) -> None:
    document_path = tmp_path / "case.txt"
    document_path.write_text(
        "Services\n\nThe student receives daily reading intervention.\n\nTransportation is provided by bus.",
        encoding="utf-8",
    )
    response_text = (
        "The student receives daily reading intervention.\n"
        "Transportation is provided by bus.\n"
        "Extended time is available."
    )

    scanned_document = DocumentScanner().scan_path(document_path)
    report = TraceAnalysisPipeline().analyze_response("case-1", response_text, [scanned_document])

    assert len(report.assessments) == 3
    assert report.assessments[0].claim.claim_id == "claim-1"
    assert report.assessments[0].metadata["retrieval_metadata"]["chunk_count"] > 0
    assert "claim_extraction_metrics" in report.metadata
    assert report.summary is not None
    assert report.summary.total_claims == 3
    assert report.findings
