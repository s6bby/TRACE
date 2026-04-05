"""CLI for TRACE claim extraction."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from trace_backend.claims import ClaimExtractionConfig, extract_claims


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
    parser = argparse.ArgumentParser(description="Run TRACE claim extraction.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", type=Path, help="Path to a text file containing the raw model response.")
    group.add_argument("--text", type=str, help="Raw model response text.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the resulting JSON.")
    args = parser.parse_args()

    response_text = args.text if args.text is not None else args.path.read_text(encoding="utf-8")
    result = extract_claims(response_text, config=ClaimExtractionConfig())
    payload = _serialize(result)

    if args.pretty:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload))


if __name__ == "__main__":
    main()
