"""CLI for running the TRACE backend pipeline end to end."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from trace_backend.pipeline.orchestrator import TraceAnalysisPipeline
from trace_backend.scanning import DocumentScanner


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TRACE retrieval and evaluation pipeline.")
    parser.add_argument("--case-id", type=str, default="analysis", help="Identifier for the evaluation case.")
    parser.add_argument(
        "--response-path",
        type=Path,
        required=True,
        help="Path to a text file containing the raw model response.",
    )
    parser.add_argument(
        "--document",
        action="append",
        dest="documents",
        required=True,
        help="Path to a source document. Repeat for multiple files.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the resulting JSON.")
    args = parser.parse_args()

    scanner = DocumentScanner()
    scanned_documents = [scanner.scan_path(path) for path in args.documents]
    response_text = args.response_path.read_text(encoding="utf-8")

    pipeline = TraceAnalysisPipeline()
    report = pipeline.analyze_response(args.case_id, response_text, scanned_documents)
    payload = _serialize(report)

    if args.pretty:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload))


if __name__ == "__main__":
    main()
