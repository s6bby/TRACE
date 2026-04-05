"""Reliability report generation stage."""

from __future__ import annotations

from trace_core.schemas import ClaimAssessment, ReliabilityReport


def build_report(case_id: str, assessments: list[ClaimAssessment]) -> ReliabilityReport:
    """Assemble a reliability report from claim assessments."""
    return ReliabilityReport(case_id=case_id, assessments=assessments)
