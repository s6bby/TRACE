"""Chunk scanned documents into retrieval units."""

from __future__ import annotations

from pathlib import Path

from trace_backend.retrieval.models import RetrievalChunk
from trace_backend.retrieval.utils import normalize_text
from trace_backend.scanning.models import DocumentScanResult


def _document_id(path: Path) -> str:
    return path.stem


def build_retrieval_chunks(
    documents: list[DocumentScanResult],
    *,
    include_tables: bool = True,
    max_chunk_chars: int = 1000,
) -> list[RetrievalChunk]:
    """Build retrieval chunks from scanned document blocks."""

    chunks: list[RetrievalChunk] = []

    for document in documents:
        doc_id = _document_id(document.source_path)
        current_section: str | None = None

        for block_index, block in enumerate(document.blocks, start=1):
            if block.kind == "heading":
                current_section = normalize_text(block.text)

            if block.kind == "table" and not include_tables:
                continue
            if block.kind == "image" and not normalize_text(block.text):
                continue

            chunk_text = normalize_text(block.text)
            if not chunk_text:
                continue

            if len(chunk_text) > max_chunk_chars:
                chunk_text = chunk_text[:max_chunk_chars].rstrip() + " ..."

            index_parts = [current_section or "", chunk_text]
            index_text = normalize_text("\n".join(part for part in index_parts if part))

            chunks.append(
                RetrievalChunk(
                    chunk_id=f"{doc_id}-chunk-{len(chunks) + 1}",
                    document_id=doc_id,
                    source_path=document.source_path,
                    text=chunk_text,
                    index_text=index_text,
                    page_number=block.page_number,
                    section=current_section,
                    block_kind=block.kind,
                    metadata={
                        "block_id": block.block_id,
                        "extractor": block.extractor,
                        "page_number": block.page_number,
                    },
                )
            )

    return chunks
