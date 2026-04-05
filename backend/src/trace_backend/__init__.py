"""TRACE backend package."""

from trace_backend.claims import (
    Claim,
    ClaimExtractionConfig,
    ClaimExtractionResult,
    ClaimExtractor,
    extract_claims,
)
from trace_backend.evaluation import EvaluationConfig, MultiJudgeEvaluator, OpenAICompatibleJudge
from trace_backend.pipeline import ReliabilityReport
from trace_backend.pipeline.orchestrator import TraceAnalysisPipeline
from trace_backend.retrieval import (
    HybridEvidenceRetriever,
    OpenAICompatibleEmbeddingProvider,
    RetrievalConfig,
)
from trace_backend.scanning import DocumentScanResult, DocumentScanner, ScanConfig

__all__ = [
    "Claim",
    "ClaimExtractionConfig",
    "ClaimExtractionResult",
    "ClaimExtractor",
    "DocumentScanResult",
    "DocumentScanner",
    "EvaluationConfig",
    "HybridEvidenceRetriever",
    "MultiJudgeEvaluator",
    "OpenAICompatibleEmbeddingProvider",
    "OpenAICompatibleJudge",
    "ReliabilityReport",
    "RetrievalConfig",
    "ScanConfig",
    "TraceAnalysisPipeline",
    "extract_claims",
]
