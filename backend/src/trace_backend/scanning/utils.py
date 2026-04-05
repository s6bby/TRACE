"""Utility helpers for TRACE document scanning."""

from __future__ import annotations

from difflib import SequenceMatcher
import re
from typing import Iterable

from charset_normalizer import from_bytes

from trace_backend.scanning.models import ContentBlock

WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse whitespace while preserving the visible token sequence."""

    return WHITESPACE_RE.sub(" ", text or "").strip()


def similarity_ratio(left: str, right: str) -> float:
    """Return a normalized similarity ratio between two text strings."""

    return SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def decode_text_bytes(raw: bytes) -> tuple[str, str]:
    """Decode bytes with charset detection and conservative fallbacks."""

    best = from_bytes(raw).best()
    if best is not None:
        return str(best), best.encoding or "unknown"

    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "latin-1"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="ignore"), "utf-8-ignore"


def table_to_markdown(rows: list[list[str]]) -> str:
    """Render a table as markdown for downstream retrieval and review."""

    if not rows:
        return ""

    width = max(len(row) for row in rows)
    normalized_rows = [
        [normalize_text(cell) for cell in row] + [""] * (width - len(row))
        for row in rows
    ]

    header = normalized_rows[0]
    divider = ["---"] * width
    body = normalized_rows[1:] or [[""] * width]

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(divider) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def merge_block_text(blocks: Iterable[ContentBlock]) -> str:
    """Join ordered blocks into a single document text string."""

    chunks = [normalize_text(block.text) for block in blocks if normalize_text(block.text)]
    return "\n\n".join(chunks)


def list_item_text(text: str) -> bool:
    """Return whether the block text resembles a list item."""

    stripped = text.lstrip()
    return stripped.startswith(("-", "*", "\u2022")) or bool(
        re.match(r"^\d+[.)]\s+", stripped)
    )
