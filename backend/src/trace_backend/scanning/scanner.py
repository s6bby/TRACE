"""Dispatcher for TRACE document scanning."""

from __future__ import annotations

from pathlib import Path

from trace_backend.scanning.docx import scan_docx_document
from trace_backend.scanning.models import DocumentScanResult, ScanConfig
from trace_backend.scanning.pdf import scan_pdf_document
from trace_backend.scanning.text import scan_text_document


class DocumentScanner:
    """Scan supported document types into a normalized TRACE representation."""

    def __init__(self, config: ScanConfig | None = None) -> None:
        self.config = config or ScanConfig()

    def scan_path(self, path: str | Path) -> DocumentScanResult:
        source_path = Path(path).expanduser().resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"Document not found: {source_path}")

        suffix = source_path.suffix.lower()
        if suffix == ".pdf":
            return scan_pdf_document(source_path, self.config)
        if suffix == ".docx":
            return scan_docx_document(source_path, self.config)
        if suffix == ".txt":
            return scan_text_document(source_path, self.config)

        raise ValueError(
            f"Unsupported file type '{suffix}'. TRACE currently supports PDF, DOCX, and TXT."
        )
