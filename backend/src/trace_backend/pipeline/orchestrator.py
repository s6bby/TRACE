"""High-level orchestration for TRACE retrieval and evaluation."""

from __future__ import annotations

from trace_backend.claims import ClaimExtractionConfig, ClaimExtractor
from trace_backend.evaluation import EvaluationConfig, MultiJudgeEvaluator
from trace_backend.pipeline.models import ReliabilityReport
from trace_backend.pipeline.reporting import build_reliability_report
from trace_backend.retrieval import HybridEvidenceRetriever, OpenAICompatibleEmbeddingProvider, RetrievalConfig
from trace_backend.scanning.models import DocumentScanResult


class TraceAnalysisPipeline:
    """Run claim extraction, retrieval, and evaluation over scanned documents."""

    def __init__(
        self,
        *,
        claim_config: ClaimExtractionConfig | None = None,
        retrieval_config: RetrievalConfig | None = None,
        evaluation_config: EvaluationConfig | None = None,
    ) -> None:
        self.claim_extractor = ClaimExtractor(claim_config)
        self.retrieval_config = retrieval_config or RetrievalConfig()
        self.evaluation_config = evaluation_config or EvaluationConfig()

    def analyze_response(
        self,
        case_id: str,
        response_text: str,
        documents: list[DocumentScanResult],
    ) -> ReliabilityReport:
        claim_result = self.claim_extractor.extract(response_text)
        embedding_provider = OpenAICompatibleEmbeddingProvider.from_env()
        retriever = HybridEvidenceRetriever(
            documents,
            config=self.retrieval_config,
            embedding_provider=embedding_provider,
        )
        evaluator = MultiJudgeEvaluator(config=self.evaluation_config)

        assessments = []
        retrieval_results = retriever.retrieve_many(claim_result.claims, top_k=self.retrieval_config.top_k)
        for retrieval_result in retrieval_results:
            assessment = evaluator.evaluate(retrieval_result.claim, retrieval_result.evidence)
            assessment.metadata.update(
                {
                    "retrieval_candidates": retrieval_result.evidence,
                    "retrieval_findings": retrieval_result.findings,
                    "retrieval_metadata": retrieval_result.metadata,
                }
            )
            assessments.append(assessment)

        return build_reliability_report(
            case_id=case_id,
            documents=documents,
            claim_result=claim_result,
            assessments=assessments,
        )
