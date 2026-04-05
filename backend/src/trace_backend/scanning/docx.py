"""DOCX extraction for TRACE document scanning."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from trace_backend.scanning.models import (
    ContentBlock,
    DocumentMetrics,
    DocumentScanResult,
    ExtractorTrace,
    PageScan,
    ScanConfig,
    ScanFinding,
    TableContent,
)
from trace_backend.scanning.ocr import ocr_image_bytes
from trace_backend.scanning.utils import list_item_text, merge_block_text, normalize_text, table_to_markdown


def _paragraph_kind(paragraph: Paragraph) -> str:
    style_name = paragraph.style.name if paragraph.style is not None else ""
    if style_name in {"Title"} or style_name.startswith("Heading"):
        return "heading"
    if "List" in style_name or list_item_text(paragraph.text):
        return "list_item"
    return "paragraph"


def _table_rows(table: Table) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in table.rows:
        cells: list[str] = []
        for cell in row.cells:
            joined = "\n".join(paragraph.text for paragraph in cell.paragraphs)
            cells.append(normalize_text(joined))
        if any(cells):
            rows.append(cells)
    return rows


def _paragraph_image_relationship_ids(paragraph: Paragraph) -> list[str]:
    relationship_ids: list[str] = []
    seen: set[str] = set()

    for blip in paragraph._element.xpath(".//a:blip"):
        relationship_id = blip.get(qn("r:embed"))
        if relationship_id and relationship_id not in seen:
            seen.add(relationship_id)
            relationship_ids.append(relationship_id)

    return relationship_ids


def _document_image_relationship_ids(document: Document) -> list[str]:
    return [
        relationship_id
        for relationship_id, relationship in document.part.rels.items()
        if relationship.reltype == RT.IMAGE
    ]


def scan_docx_document(path: Path, config: ScanConfig) -> DocumentScanResult:
    """Scan a DOCX document preserving paragraph and table order."""

    document = Document(path)
    blocks: list[ContentBlock] = []
    tables: list[TableContent] = []
    findings: list[ScanFinding] = []
    processed_image_ids: set[str] = set()
    ocr_fragments: list[str] = []

    for index, item in enumerate(document.iter_inner_content(), start=1):
        if isinstance(item, Paragraph):
            text = normalize_text(item.text)
            if text:
                blocks.append(
                    ContentBlock(
                        block_id=f"docx-block-{index}",
                        kind=_paragraph_kind(item),
                        text=text,
                        page_number=1,
                        extractor="python-docx",
                        metadata={"style": item.style.name if item.style is not None else ""},
                    )
                )

            for image_index, relationship_id in enumerate(
                _paragraph_image_relationship_ids(item),
                start=1,
            ):
                processed_image_ids.add(relationship_id)
                image_part = document.part.related_parts.get(relationship_id)
                part_name = str(getattr(image_part, "partname", relationship_id))
                ocr_text = ""
                ocr_attempted = False

                if image_part is not None and config.enable_ocr and config.ocr_on_docx_images:
                    ocr_attempted = True
                    try:
                        ocr_text = ocr_image_bytes(image_part.blob)
                    except Exception as exc:  # pragma: no cover - defensive safeguard
                        findings.append(
                            ScanFinding(
                                code="docx-image-ocr-failed",
                                severity="warning",
                                message=(
                                    "OCR failed on an embedded DOCX image. Manual or multimodal "
                                    "review is recommended for this graphic."
                                ),
                                page_number=1,
                                metadata={
                                    "relationship_id": relationship_id,
                                    "part_name": part_name,
                                    "error": str(exc),
                                },
                            )
                        )

                if ocr_text:
                    ocr_fragments.append(ocr_text)
                    findings.append(
                        ScanFinding(
                            code="docx-image-ocr-used",
                            severity="info",
                            message=(
                                "OCR recovered text from an embedded DOCX image so it can be "
                                "included in downstream retrieval."
                            ),
                            page_number=1,
                            metadata={
                                "relationship_id": relationship_id,
                                "part_name": part_name,
                                "character_count": len(ocr_text),
                            },
                        )
                    )
                elif ocr_attempted:
                    findings.append(
                        ScanFinding(
                            code="docx-image-ocr-empty",
                            severity="warning",
                            message=(
                                "An embedded DOCX image produced no OCR text. Charts, graphics, "
                                "or low-quality scans may still require multimodal review."
                            ),
                            page_number=1,
                            metadata={"relationship_id": relationship_id, "part_name": part_name},
                        )
                    )

                blocks.append(
                    ContentBlock(
                        block_id=f"docx-image-{index}-{image_index}",
                        kind="image",
                        text=ocr_text,
                        page_number=1,
                        extractor="rapidocr" if ocr_attempted else "python-docx",
                        metadata={
                            "relationship_id": relationship_id,
                            "part_name": part_name,
                            "ocr_attempted": ocr_attempted,
                            "source_index": index,
                        },
                    )
                )
            continue

        if isinstance(item, Table):
            rows = _table_rows(item)
            if not rows:
                continue

            markdown = table_to_markdown(rows[: config.max_logged_table_rows])
            table = TableContent(
                table_id=f"docx-table-{len(tables) + 1}",
                page_number=1,
                rows=rows,
                markdown=markdown,
                extractor="python-docx",
                metadata={"row_count": len(rows)},
            )
            tables.append(table)
            blocks.append(
                ContentBlock(
                    block_id=f"docx-table-block-{len(tables)}",
                    kind="table",
                    text=markdown,
                    page_number=1,
                    extractor="python-docx",
                    metadata={"table_id": table.table_id},
                )
            )

    all_image_relationship_ids = _document_image_relationship_ids(document)
    for fallback_index, relationship_id in enumerate(all_image_relationship_ids, start=1):
        if relationship_id in processed_image_ids:
            continue

        image_part = document.part.related_parts.get(relationship_id)
        part_name = str(getattr(image_part, "partname", relationship_id))
        ocr_text = ""
        ocr_attempted = False

        if image_part is not None and config.enable_ocr and config.ocr_on_docx_images:
            ocr_attempted = True
            try:
                ocr_text = ocr_image_bytes(image_part.blob)
            except Exception as exc:  # pragma: no cover - defensive safeguard
                findings.append(
                    ScanFinding(
                        code="docx-image-ocr-failed",
                        severity="warning",
                        message=(
                            "OCR failed on an embedded DOCX image. Manual or multimodal review "
                            "is recommended for this graphic."
                        ),
                        page_number=1,
                        metadata={
                            "relationship_id": relationship_id,
                            "part_name": part_name,
                            "error": str(exc),
                        },
                    )
                )

        if ocr_text:
            ocr_fragments.append(ocr_text)

        blocks.append(
            ContentBlock(
                block_id=f"docx-image-fallback-{fallback_index}",
                kind="image",
                text=ocr_text,
                page_number=1,
                extractor="rapidocr" if ocr_attempted else "python-docx",
                metadata={
                    "relationship_id": relationship_id,
                    "part_name": part_name,
                    "ocr_attempted": ocr_attempted,
                    "fallback_ordering": True,
                },
            )
        )
        findings.append(
            ScanFinding(
                code="docx-unplaced-image",
                severity="warning",
                message=(
                    "An embedded DOCX image could not be mapped cleanly into body order and was "
                    "appended after the main content. Review its placement before citing it."
                ),
                page_number=1,
                metadata={"relationship_id": relationship_id, "part_name": part_name},
            )
        )

    image_count = len(all_image_relationship_ids)
    if image_count:
        findings.append(
            ScanFinding(
                code="docx-inline-images-present",
                severity="warning",
                message=(
                    "The DOCX contains embedded images or graphics. TRACE attempts OCR on those "
                    "images, but charts and non-text visuals can still require multimodal review."
                ),
                page_number=1,
                metadata={"image_count": image_count},
            )
        )

    page_text = merge_block_text(blocks)
    page = PageScan(
        page_number=1,
        text=page_text,
        blocks=blocks,
        tables=tables,
        image_count=image_count,
        metadata={"inline_shape_count": image_count},
    )
    trace = ExtractorTrace(
        extractor="python-docx",
        page_texts=[page_text],
        metadata={"inline_shape_count": image_count},
    )
    extractor_traces = [trace]
    if image_count:
        extractor_traces.append(
            ExtractorTrace(
                extractor="rapidocr",
                page_texts=["\n\n".join(ocr_fragments)],
                metadata={"image_count": image_count},
            )
        )

    return DocumentScanResult(
        source_path=path,
        file_kind="docx",
        text=page_text,
        pages=[page],
        blocks=blocks,
        tables=tables,
        findings=findings,
        extractor_traces=extractor_traces,
        verification=None,
        metrics=DocumentMetrics(
            page_count=1,
            block_count=len(blocks),
            table_count=len(tables),
            image_count=image_count,
            character_count=len(normalize_text(page_text)),
            ocr_recommended_pages=[1] if image_count else [],
        ),
        metadata={
            "title": document.core_properties.title,
            "author": document.core_properties.author,
            "revision": document.core_properties.revision,
        },
    )
