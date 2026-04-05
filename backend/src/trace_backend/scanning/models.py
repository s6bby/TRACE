"""Structured models for document scanning results."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

BlockKind = Literal["heading", "paragraph", "list_item", "table", "image", "metadata"]
FileKind = Literal["pdf", "docx", "txt"]
Severity = Literal["info", "warning", "error"]


@dataclass(slots=True)
class ContentBlock:
    """A normalized content block extracted from a document."""

    block_id: str
    kind: BlockKind
    text: str
    page_number: int | None
    extractor: str
    bbox: tuple[float, float, float, float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TableContent:
    """A normalized table extracted from a document."""

    table_id: str
    page_number: int | None
    rows: list[list[str]]
    markdown: str
    extractor: str
    bbox: tuple[float, float, float, float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PageScan:
    """Structured content and metrics for one logical page."""

    page_number: int
    text: str
    blocks: list[ContentBlock] = field(default_factory=list)
    tables: list[TableContent] = field(default_factory=list)
    image_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExtractorTrace:
    """Raw extractor output retained for verification and debugging."""

    extractor: str
    page_texts: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExtractorComparison:
    """Agreement metrics between two extractors for a page."""

    extractor_a: str
    extractor_b: str
    page_number: int
    similarity: float
    char_count_a: int
    char_count_b: int


@dataclass(slots=True)
class ScanFinding:
    """A scanner finding that may affect downstream reliability."""

    code: str
    severity: Severity
    message: str
    page_number: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VerificationReport:
    """Cross-extractor agreement and verification metadata."""

    primary_extractor: str
    supporting_extractors: list[str]
    comparisons: list[ExtractorComparison] = field(default_factory=list)


@dataclass(slots=True)
class DocumentMetrics:
    """Summary metrics for a scanned document."""

    page_count: int
    block_count: int
    table_count: int
    image_count: int
    character_count: int
    ocr_recommended_pages: list[int] = field(default_factory=list)


@dataclass(slots=True)
class DocumentScanResult:
    """Normalized scanner output consumed by later TRACE stages."""

    source_path: Path
    file_kind: FileKind
    text: str
    pages: list[PageScan]
    blocks: list[ContentBlock]
    tables: list[TableContent]
    findings: list[ScanFinding]
    extractor_traces: list[ExtractorTrace]
    verification: VerificationReport | None
    metrics: DocumentMetrics
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ScanConfig:
    """Configuration for the TRACE document scanner."""

    similarity_warning_threshold: float = 0.82
    low_text_page_threshold: int = 120
    max_logged_table_rows: int = 50
    enable_ocr: bool = True
    ocr_on_docx_images: bool = True
    ocr_on_pdf_pages: bool = True
