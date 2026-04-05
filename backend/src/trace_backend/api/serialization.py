"""Serialization helpers for TRACE API and CLIs."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def serialize(value: Any) -> Any:
    """Recursively serialize dataclasses and paths into JSON-safe values."""

    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return serialize(asdict(value))
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize(item) for item in value]
    return value
