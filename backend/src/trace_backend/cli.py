"""Simple CLI for the TRACE document scanner."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from trace_backend.scanning import DocumentScanner, ScanConfig


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
    parser = argparse.ArgumentParser(description="Run TRACE document scanning.")
    parser.add_argument("path", type=Path, help="Path to a PDF, DOCX, or TXT file.")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the resulting JSON.",
    )
    args = parser.parse_args()

    scanner = DocumentScanner(ScanConfig())
    result = scanner.scan_path(args.path)
    payload = _serialize(result)

    if args.pretty:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload))


if __name__ == "__main__":
    main()
