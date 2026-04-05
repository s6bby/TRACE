from __future__ import annotations

from pathlib import Path

from trace_backend.benchmark.runner import run_benchmark


def test_run_benchmark_on_synthetic_dataset() -> None:
    dataset = Path("backend/data/synthetic-eval")
    result = run_benchmark(dataset)

    assert result.summary.case_count == 3
    assert result.summary.total_gold_claims == 9
    assert result.summary.total_predicted_claims >= 9
    assert result.summary.total_matched_claims >= 8
    assert result.summary.claim_recall > 0.8
    assert result.summary.retrieval_recall_at_k > 0.7
