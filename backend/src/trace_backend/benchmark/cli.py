"""CLI for running the TRACE synthetic benchmark."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from trace_backend.benchmark.runner import run_benchmark


def _serialize(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return _serialize(asdict(value))
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


def _write_csv(csv_path: Path, cases: list[dict[str, Any]]) -> None:
    if not cases:
        return

    fieldnames = [
        "case_id",
        "gold_claim_count",
        "predicted_claim_count",
        "matched_claim_count",
        "claim_precision",
        "claim_recall",
        "label_accuracy",
        "retrieval_recall_at_k",
        "citation_validity_rate",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            writer.writerow({field: case.get(field) for field in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TRACE synthetic benchmark.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("backend/data/synthetic-eval"),
        help="Path to the synthetic benchmark dataset.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the resulting JSON.")
    parser.add_argument("--csv", type=Path, help="Optional CSV output path for per-case metrics.")
    args = parser.parse_args()

    result = run_benchmark(args.dataset)
    payload = _serialize(result)

    if args.csv:
        _write_csv(args.csv, payload["cases"])

    if args.pretty:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload))


if __name__ == "__main__":
    main()
