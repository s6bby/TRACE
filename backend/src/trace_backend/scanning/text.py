"""TXT file extraction for TRACE document scanning."""

from __future__ import annotations

from pathlib import Path

from trace_backend.scanning.models import (
    ContentBlock,
    DocumentMetrics,
    DocumentScanResult,
    ExtractorTrace,
    PageScan,
    ScanConfig,
)
from trace_backend.scanning.utils import decode_text_bytes, list_item_text, merge_block_text, normalize_text


def _classify_text_block(text: str) -> str:
    if list_item_text(text):
        return "list_item"
    if len(text) <= 100 and text == text.upper():
        return "heading"
    return "paragraph"


def scan_text_document(path: Path, config: ScanConfig) -> DocumentScanResult:
    """Scan a plain-text document into normalized blocks."""

    del config

    raw = path.read_bytes()
    decoded, encoding = decode_text_bytes(raw)
    paragraphs = [chunk.strip() for chunk in decoded.split("\n\n") if chunk.strip()]
    blocks: list[ContentBlock] = []

    for index, chunk in enumerate(paragraphs, start=1):
        blocks.append(
            ContentBlock(
                block_id=f"txt-block-{index}",
                kind=_classify_text_block(chunk),
                text=chunk,
                page_number=1,
                extractor="plain-text",
                metadata={"paragraph_index": index},
            )
        )

    page_text = merge_block_text(blocks)
    page = PageScan(
        page_number=1,
        text=page_text,
        blocks=blocks,
        metadata={"encoding": encoding},
    )
    trace = ExtractorTrace(extractor="plain-text", page_texts=[page_text], metadata={"encoding": encoding})

    return DocumentScanResult(
        source_path=path,
        file_kind="txt",
        text=page_text,
        pages=[page],
        blocks=blocks,
        tables=[],
        findings=[],
        extractor_traces=[trace],
        verification=None,
        metrics=DocumentMetrics(
            page_count=1,
            block_count=len(blocks),
            table_count=0,
            image_count=0,
            character_count=len(normalize_text(page_text)),
            ocr_recommended_pages=[],
        ),
        metadata={"encoding": encoding},
    )
