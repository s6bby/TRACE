"""Synthetic benchmark harness for TRACE."""

from __future__ import annotations
import json
from pathlib import Path

from trace_backend.benchmark.models import (
    BenchmarkCase,
    BenchmarkCaseResult,
    BenchmarkResult,
    BenchmarkSummary,
    GoldClaim,
)
from trace_backend.pipeline.orchestrator import TraceAnalysisPipeline
from trace_backend.retrieval.utils import normalize_text
from trace_backend.scanning import DocumentScanner


def _load_case(case_dir: Path) -> BenchmarkCase:
    with (case_dir / "gold.json").open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    documents = sorted((case_dir / "documents").iterdir())
    gold_claims = [
        GoldClaim(
            text=item["text"],
            label=item["label"],
            evidence_substrings=item.get("evidence_substrings", []),
        )
        for item in payload["claims"]
    ]
    return BenchmarkCase(
        case_id=payload["case_id"],
        documents=documents,
        response_path=case_dir / "response.txt",
        gold_claims=gold_claims,
    )


def load_benchmark_cases(dataset_path: Path) -> list[BenchmarkCase]:
    """Load benchmark cases from a dataset directory."""

    return [
        _load_case(case_dir)
        for case_dir in sorted(dataset_path.iterdir())
        if case_dir.is_dir()
    ]


def _evidence_contains_substring(assessment, substring: str) -> bool:
    normalized_target = normalize_text(substring).lower()
    retrieval_candidates = assessment.metadata.get("retrieval_candidates", [])
    for candidate in retrieval_candidates:
        if normalized_target in normalize_text(candidate.snippet).lower():
            return True
    return False


def _case_result(case: BenchmarkCase, pipeline: TraceAnalysisPipeline) -> BenchmarkCaseResult:
    scanner = DocumentScanner()
    scanned_documents = [scanner.scan_path(path) for path in case.documents]
    response_text = case.response_path.read_text(encoding="utf-8")
    report = pipeline.analyze_response(case.case_id, response_text, scanned_documents)

    predicted_by_text = {
        normalize_text(assessment.claim.text): assessment
        for assessment in report.assessments
    }
    gold_by_text = {
        normalize_text(claim.text): claim
        for claim in case.gold_claims
    }

    matched_keys = sorted(set(predicted_by_text) & set(gold_by_text))
    matched_claim_count = len(matched_keys)
    label_correct = 0
    retrieval_hits = 0
    citation_valid_claims = 0

    for key in matched_keys:
        assessment = predicted_by_text[key]
        gold = gold_by_text[key]

        if assessment.label == gold.label:
            label_correct += 1

        if not gold.evidence_substrings:
            retrieval_hits += 1
        else:
            if all(_evidence_contains_substring(assessment, substring) for substring in gold.evidence_substrings):
                retrieval_hits += 1

        if not any(finding.severity == "error" for finding in assessment.validation_findings):
            citation_valid_claims += 1

    gold_claim_count = len(case.gold_claims)
    predicted_claim_count = len(report.assessments)
    claim_precision = matched_claim_count / predicted_claim_count if predicted_claim_count else 0.0
    claim_recall = matched_claim_count / gold_claim_count if gold_claim_count else 0.0
    label_accuracy = label_correct / matched_claim_count if matched_claim_count else 0.0
    retrieval_recall_at_k = retrieval_hits / matched_claim_count if matched_claim_count else 0.0
    citation_validity_rate = citation_valid_claims / matched_claim_count if matched_claim_count else 0.0

    return BenchmarkCaseResult(
        case_id=case.case_id,
        gold_claim_count=gold_claim_count,
        predicted_claim_count=predicted_claim_count,
        matched_claim_count=matched_claim_count,
        claim_precision=claim_precision,
        claim_recall=claim_recall,
        label_accuracy=label_accuracy,
        retrieval_recall_at_k=retrieval_recall_at_k,
        citation_validity_rate=citation_validity_rate,
        metadata={
            "report_summary": report.summary,
        },
    )


def run_benchmark(dataset_path: str | Path) -> BenchmarkResult:
    """Run the TRACE benchmark over a dataset directory."""

    dataset = Path(dataset_path).expanduser().resolve()
    cases = load_benchmark_cases(dataset)
    pipeline = TraceAnalysisPipeline()
    case_results = [_case_result(case, pipeline) for case in cases]

    total_gold_claims = sum(case.gold_claim_count for case in case_results)
    total_predicted_claims = sum(case.predicted_claim_count for case in case_results)
    total_matched_claims = sum(case.matched_claim_count for case in case_results)

    summary = BenchmarkSummary(
        case_count=len(case_results),
        total_gold_claims=total_gold_claims,
        total_predicted_claims=total_predicted_claims,
        total_matched_claims=total_matched_claims,
        claim_precision=(
            total_matched_claims / total_predicted_claims
            if total_predicted_claims
            else 0.0
        ),
        claim_recall=(
            total_matched_claims / total_gold_claims
            if total_gold_claims
            else 0.0
        ),
        label_accuracy=(
            sum(case.label_accuracy * case.matched_claim_count for case in case_results) / total_matched_claims
            if total_matched_claims
            else 0.0
        ),
        retrieval_recall_at_k=(
            sum(case.retrieval_recall_at_k * case.matched_claim_count for case in case_results)
            / total_matched_claims
            if total_matched_claims
            else 0.0
        ),
        citation_validity_rate=(
            sum(case.citation_validity_rate * case.matched_claim_count for case in case_results)
            / total_matched_claims
            if total_matched_claims
            else 0.0
        ),
    )

    return BenchmarkResult(dataset_path=dataset, cases=case_results, summary=summary)
