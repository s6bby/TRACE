"""Optional OCR backstop for image-heavy scanned pages."""

from __future__ import annotations

from functools import lru_cache

import fitz
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from trace_backend.scanning.utils import normalize_text


@lru_cache(maxsize=1)
def _rapidocr_engine() -> RapidOCR:
    return RapidOCR()


def _ordered_ocr_text(img_content: str | np.ndarray | bytes) -> str:
    results, _elapsed = _rapidocr_engine()(img_content)
    if not results:
        return ""

    ordered_lines = sorted(
        results,
        key=lambda item: (
            min(point[1] for point in item[0]),
            min(point[0] for point in item[0]),
        ),
    )
    return normalize_text("\n".join(item[1] for item in ordered_lines if item[1].strip()))


def ocr_image_bytes(image_bytes: bytes) -> str:
    """Run OCR over raw image bytes."""

    return _ordered_ocr_text(image_bytes)


def ocr_pdf_page(page: fitz.Page, zoom: float = 2.0) -> str:
    """Run OCR over a rendered PDF page and return normalized text."""

    pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
        pixmap.height,
        pixmap.width,
        pixmap.n,
    )
    return _ordered_ocr_text(image)
