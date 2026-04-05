"""Models and configuration for TRACE evidence retrieval."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RetrievalChunk:
    """A searchable chunk derived from scanned document content."""

    chunk_id: str
    document_id: str
    source_path: Path
    text: str
    index_text: str
    page_number: int | None
    section: str | None
    block_kind: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievalConfig:
    """Configuration for hybrid evidence retrieval."""

    top_k: int = 5
    lexical_weight: float = 0.65
    semantic_weight: float = 0.35
    rrf_constant: int = 60
    max_chunk_chars: int = 1000
    include_tables: bool = True
    min_lexical_score: float = 0.05
    section_heading_boost: float = 0.08
    number_overlap_boost: float = 0.12
    phrase_overlap_boost: float = 0.1
