"""TRACE claim extraction utilities."""

from trace_backend.claims.extractor import ClaimExtractor, extract_claims
from trace_backend.claims.models import (
    Claim,
    ClaimExtractionConfig,
    ClaimExtractionMetrics,
    ClaimExtractionResult,
    ClaimFinding,
    TextSpan,
)

__all__ = [
    "Claim",
    "ClaimExtractionConfig",
    "ClaimExtractionMetrics",
    "ClaimExtractionResult",
    "ClaimExtractor",
    "ClaimFinding",
    "TextSpan",
    "extract_claims",
]
