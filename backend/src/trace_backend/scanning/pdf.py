"""PDF extraction and cross-checking for TRACE document scanning."""

from __future__ import annotations

from statistics import median
from pathlib import Path

import fitz
import pdfplumber

from trace_backend.scanning.models import (
    ContentBlock,
    DocumentMetrics,
    DocumentScanResult,
    ExtractorComparison,
    ExtractorTrace,
    PageScan,
    ScanConfig,
    ScanFinding,
    TableContent,
    VerificationReport,
)
from trace_backend.scanning.ocr import ocr_pdf_page
from trace_backend.scanning.utils import merge_block_text, normalize_text, similarity_ratio, table_to_markdown

PDF_TABLE_SETTINGS: tuple[dict[str, object], ...] = (
    {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
    {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "snap_tolerance": 4,
        "join_tolerance": 4,
        "intersection_tolerance": 5,
        "text_x_tolerance": 3,
        "text_y_tolerance": 3,
    },
)


def _is_list_item(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith(("-", "*", "\u2022")) or (
        len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in {".", ")"}
    )


def _pdf_block_kind(text: str, average_font_size: float, baseline_font_size: float) -> str:
    if _is_list_item(text):
        return "list_item"
    if len(text) <= 160 and average_font_size >= baseline_font_size * 1.2:
        return "heading"
    return "paragraph"


def _extract_pymupdf_blocks(page: fitz.Page, page_number: int) -> tuple[list[ContentBlock], int, str]:
    page_dict = page.get_text("dict", sort=True)
    candidates: list[dict[str, object]] = []
    font_sizes: list[float] = []
    image_count = 0

    for block_index, raw_block in enumerate(page_dict.get("blocks", []), start=1):
        block_type = raw_block.get("type", 0)
        if block_type == 1:
            image_count += 1
            continue
        if block_type != 0:
            continue

        fragments: list[str] = []
        span_sizes: list[float] = []
        for line in raw_block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                if not text or not text.strip():
                    continue
                fragments.append(text)
                span_sizes.append(float(span.get("size", 0.0)))

        joined = normalize_text(" ".join(fragments))
        if not joined:
            continue

        font_sizes.extend(size for size in span_sizes if size > 0)
        candidates.append(
            {
                "block_index": block_index,
                "text": joined,
                "bbox": tuple(float(value) for value in raw_block.get("bbox", (0, 0, 0, 0))),
                "average_font_size": (sum(span_sizes) / len(span_sizes)) if span_sizes else 0.0,
            }
        )

    baseline_font_size = median(font_sizes) if font_sizes else 11.0
    blocks = [
        ContentBlock(
            block_id=f"pdf-text-{page_number}-{candidate['block_index']}",
            kind=_pdf_block_kind(
                candidate["text"],  # type: ignore[arg-type]
                float(candidate["average_font_size"]),
                baseline_font_size,
            ),
            text=str(candidate["text"]),
            page_number=page_number,
            extractor="pymupdf",
            bbox=candidate["bbox"],  # type: ignore[arg-type]
            metadata={"average_font_size": float(candidate["average_font_size"])},
        )
        for candidate in candidates
    ]

    plain_text = normalize_text(page.get_text("text", sort=True))
    return blocks, image_count, plain_text


def _extract_pdfplumber_tables(plumber_page: pdfplumber.page.Page, page_number: int, config: ScanConfig) -> list[TableContent]:
    tables: list[TableContent] = []
    seen_signatures: set[str] = set()

    for settings in PDF_TABLE_SETTINGS:
        for table_index, table in enumerate(plumber_page.find_tables(table_settings=settings), start=1):
            rows = table.extract()
            if not rows:
                continue

            normalized_rows = [
                [normalize_text(cell or "") for cell in row]
                for row in rows
                if any(normalize_text(cell or "") for cell in row)
            ]
            if not normalized_rows:
                continue

            markdown = table_to_markdown(normalized_rows[: config.max_logged_table_rows])
            signature = normalize_text(markdown)
            if not signature or signature in seen_signatures:
                continue

            seen_signatures.add(signature)
            tables.append(
                TableContent(
                    table_id=f"pdf-table-{page_number}-{len(tables) + 1}",
                    page_number=page_number,
                    rows=normalized_rows,
                    markdown=markdown,
                    extractor="pdfplumber",
                    bbox=tuple(float(value) for value in table.bbox),
                    metadata={"settings": settings, "table_index": table_index},
                )
            )

    return tables


def scan_pdf_document(path: Path, config: ScanConfig) -> DocumentScanResult:
    """Scan a PDF using multiple extractors and cross-check the results."""

    findings: list[ScanFinding] = []
    pages: list[PageScan] = []
    all_blocks: list[ContentBlock] = []
    all_tables: list[TableContent] = []
    comparisons: list[ExtractorComparison] = []
    primary_page_texts: list[str] = []
    verifier_page_texts: list[str] = []
    ocr_page_texts: list[str] = []
    ocr_recommended_pages: list[int] = []

    with fitz.open(path) as pymupdf_doc, pdfplumber.open(path) as plumber_doc:
        for page_index, page in enumerate(pymupdf_doc, start=1):
            pymupdf_blocks, image_count, pymupdf_plain_text = _extract_pymupdf_blocks(page, page_index)
            primary_page_texts.append(pymupdf_plain_text)

            plumber_page = plumber_doc.pages[page_index - 1]
            verifier_text = normalize_text(plumber_page.extract_text() or "")
            verifier_page_texts.append(verifier_text)

            similarity = similarity_ratio(pymupdf_plain_text, verifier_text)
            comparisons.append(
                ExtractorComparison(
                    extractor_a="pymupdf",
                    extractor_b="pdfplumber",
                    page_number=page_index,
                    similarity=similarity,
                    char_count_a=len(pymupdf_plain_text),
                    char_count_b=len(verifier_text),
                )
            )

            if similarity < config.similarity_warning_threshold and (pymupdf_plain_text or verifier_text):
                findings.append(
                    ScanFinding(
                        code="pdf-extractor-disagreement",
                        severity="warning",
                        message=(
                            "Primary and verification PDF extractors disagree on this page. "
                            "Review the original page before relying on downstream labels."
                        ),
                        page_number=page_index,
                        metadata={
                            "similarity": round(similarity, 4),
                            "primary_chars": len(pymupdf_plain_text),
                            "verification_chars": len(verifier_text),
                        },
                    )
                )

            tables = _extract_pdfplumber_tables(plumber_page, page_index, config)
            table_blocks = [
                ContentBlock(
                    block_id=f"pdf-table-block-{page_index}-{index}",
                    kind="table",
                    text=table.markdown,
                    page_number=page_index,
                    extractor="pdfplumber",
                    bbox=table.bbox,
                    metadata={"table_id": table.table_id},
                )
                for index, table in enumerate(tables, start=1)
            ]

            ocr_text = ""
            should_run_ocr = (
                config.enable_ocr
                and config.ocr_on_pdf_pages
                and image_count > 0
                and len(pymupdf_plain_text) < config.low_text_page_threshold
            )
            if should_run_ocr:
                ocr_text = ocr_pdf_page(page)
                ocr_page_texts.append(ocr_text)
                if ocr_text:
                    comparisons.append(
                        ExtractorComparison(
                            extractor_a="pymupdf",
                            extractor_b="rapidocr",
                            page_number=page_index,
                            similarity=similarity_ratio(pymupdf_plain_text, ocr_text),
                            char_count_a=len(pymupdf_plain_text),
                            char_count_b=len(ocr_text),
                        )
                    )
                    findings.append(
                        ScanFinding(
                            code="pdf-ocr-backstop-used",
                            severity="info",
                            message=(
                                "RapidOCR was used as a backstop on this page because native text "
                                "extraction looked incomplete."
                            ),
                            page_number=page_index,
                            metadata={"ocr_chars": len(ocr_text), "image_count": image_count},
                        )
                    )
                else:
                    findings.append(
                        ScanFinding(
                            code="pdf-ocr-empty-result",
                            severity="warning",
                            message=(
                                "RapidOCR was attempted on this page but did not recover text. "
                                "Manual or multimodal review is recommended."
                            ),
                            page_number=page_index,
                            metadata={"image_count": image_count},
                        )
                    )
            else:
                ocr_page_texts.append("")

            ordered_blocks = sorted(
                [
                    *pymupdf_blocks,
                    *table_blocks,
                    *(
                        [
                            ContentBlock(
                                block_id=f"pdf-ocr-{page_index}",
                                kind="paragraph",
                                text=ocr_text,
                                page_number=page_index,
                                extractor="rapidocr",
                                metadata={"ocr_backstop": True},
                            )
                        ]
                        if ocr_text and len(pymupdf_plain_text) < config.low_text_page_threshold
                        else []
                    ),
                ],
                key=lambda block: (
                    block.page_number or 0,
                    (block.bbox[1], block.bbox[0]) if block.bbox else (10_000.0, 0.0),
                ),
            )

            page_text = merge_block_text(ordered_blocks)
            if image_count > 0 and len(pymupdf_plain_text) < config.low_text_page_threshold:
                ocr_recommended_pages.append(page_index)
                findings.append(
                    ScanFinding(
                        code="pdf-ocr-recommended",
                        severity="warning",
                        message=(
                            "This page appears image-heavy or text-light. OCR or multimodal "
                            "verification is recommended before downstream validation."
                        ),
                        page_number=page_index,
                        metadata={"image_count": image_count, "primary_chars": len(pymupdf_plain_text)},
                    )
                )

            if not ordered_blocks and image_count == 0:
                findings.append(
                    ScanFinding(
                        code="pdf-empty-page",
                        severity="warning",
                        message="No text blocks or tables were extracted from this page.",
                        page_number=page_index,
                    )
                )

            pages.append(
                PageScan(
                    page_number=page_index,
                    text=page_text,
                    blocks=ordered_blocks,
                    tables=tables,
                    image_count=image_count,
                    metadata={
                        "width": float(page.rect.width),
                        "height": float(page.rect.height),
                        "extractor_similarity": similarity,
                    },
                )
            )
            all_blocks.extend(ordered_blocks)
            all_tables.extend(tables)

    document_text = "\n\n".join(page.text for page in pages if page.text)
    verification = VerificationReport(
        primary_extractor="pymupdf",
        supporting_extractors=["pdfplumber"],
        comparisons=comparisons,
    )

    return DocumentScanResult(
        source_path=path,
        file_kind="pdf",
        text=document_text,
        pages=pages,
        blocks=all_blocks,
        tables=all_tables,
        findings=findings,
        extractor_traces=[
            ExtractorTrace(extractor="pymupdf", page_texts=primary_page_texts),
            ExtractorTrace(
                extractor="pdfplumber",
                page_texts=verifier_page_texts,
                metadata={"table_strategy_count": len(PDF_TABLE_SETTINGS)},
            ),
            ExtractorTrace(extractor="rapidocr", page_texts=ocr_page_texts),
        ],
        verification=verification,
        metrics=DocumentMetrics(
            page_count=len(pages),
            block_count=len(all_blocks),
            table_count=len(all_tables),
            image_count=sum(page.image_count for page in pages),
            character_count=len(normalize_text(document_text)),
            ocr_recommended_pages=ocr_recommended_pages,
        ),
        metadata={"extractor_stack": ["pymupdf", "pdfplumber"]},
    )
