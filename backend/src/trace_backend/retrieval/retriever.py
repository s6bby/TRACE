"""Hybrid evidence retrieval for TRACE."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from trace_backend.claims.models import Claim
from trace_backend.pipeline.models import EvidenceCandidate, RetrievalFinding
from trace_backend.retrieval.chunking import build_retrieval_chunks
from trace_backend.retrieval.lexical import LexicalScorer
from trace_backend.retrieval.models import RetrievalChunk, RetrievalConfig
from trace_backend.retrieval.semantic import EmbeddingProvider, cosine_similarity_matrix
from trace_backend.scanning.models import DocumentScanResult


@dataclass(slots=True)
class RetrievalResult:
    """Retrieved evidence and retrieval findings for one claim."""

    claim: Claim
    evidence: list[EvidenceCandidate]
    findings: list[RetrievalFinding]
    metadata: dict[str, object]


class HybridEvidenceRetriever:
    """Retrieve evidence using lexical search with optional local embeddings."""

    def __init__(
        self,
        documents: list[DocumentScanResult],
        config: RetrievalConfig | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.config = config or RetrievalConfig()
        self.embedding_provider = embedding_provider
        self.chunks: list[RetrievalChunk] = build_retrieval_chunks(
            documents,
            include_tables=self.config.include_tables,
            max_chunk_chars=self.config.max_chunk_chars,
        )
        self._lexical_scorer = LexicalScorer(self.chunks)
        self._chunk_embeddings: np.ndarray | None = None

    def _ensure_chunk_embeddings(self) -> np.ndarray | None:
        if self.embedding_provider is None:
            return None
        if self._chunk_embeddings is not None:
            return self._chunk_embeddings

        chunk_texts = [chunk.index_text for chunk in self.chunks]
        self._chunk_embeddings = self.embedding_provider.embed_texts(chunk_texts)
        return self._chunk_embeddings

    def _lexical_scores(self, claim: Claim) -> list[float]:
        return [
            self._lexical_scorer.score(claim, chunk, chunk_index)
            for chunk_index, chunk in enumerate(self.chunks)
        ]

    def _semantic_scores(self, claim: Claim) -> list[float] | None:
        chunk_embeddings = self._ensure_chunk_embeddings()
        if chunk_embeddings is None:
            return None

        query_embedding = self.embedding_provider.embed_texts([claim.text])  # type: ignore[union-attr]
        similarities = cosine_similarity_matrix(query_embedding, chunk_embeddings)
        return similarities[0].tolist() if similarities.size else [0.0] * len(self.chunks)

    def _rank_scores(self, scores: list[float], minimum: float = 0.0) -> list[int]:
        ranked = [
            index
            for index, score in sorted(
                enumerate(scores),
                key=lambda item: item[1],
                reverse=True,
            )
            if score > minimum
        ]
        return ranked

    def retrieve(self, claim: Claim, top_k: int | None = None) -> RetrievalResult:
        """Retrieve the strongest evidence candidates for one claim."""

        limit = top_k or self.config.top_k
        findings: list[RetrievalFinding] = []

        if not self.chunks:
            findings.append(
                RetrievalFinding(
                    code="retrieval-empty-corpus",
                    severity="warning",
                    message="No searchable evidence chunks were available for retrieval.",
                    claim_id=claim.claim_id,
                )
            )
            return RetrievalResult(claim=claim, evidence=[], findings=findings, metadata={"chunk_count": 0})

        lexical_scores = self._lexical_scores(claim)
        semantic_scores = self._semantic_scores(claim)

        lexical_ranks = self._rank_scores(lexical_scores, minimum=self.config.min_lexical_score)
        semantic_ranks = self._rank_scores(semantic_scores or [0.0] * len(self.chunks))

        if not lexical_ranks:
            findings.append(
                RetrievalFinding(
                    code="retrieval-low-lexical-match",
                    severity="warning",
                    message=(
                        "The claim had weak lexical overlap with the document corpus. Downstream "
                        "support labels may reflect retrieval difficulty rather than claim quality."
                    ),
                    claim_id=claim.claim_id,
                )
            )

        fused_scores: dict[int, float] = {}
        for rank, chunk_index in enumerate(lexical_ranks, start=1):
            fused_scores[chunk_index] = fused_scores.get(chunk_index, 0.0) + (
                self.config.lexical_weight / (self.config.rrf_constant + rank)
            )

        for rank, chunk_index in enumerate(semantic_ranks, start=1):
            fused_scores[chunk_index] = fused_scores.get(chunk_index, 0.0) + (
                self.config.semantic_weight / (self.config.rrf_constant + rank)
            )

        if semantic_scores is None:
            findings.append(
                RetrievalFinding(
                    code="retrieval-semantic-disabled",
                    severity="info",
                    message=(
                        "No embedding provider was configured, so retrieval ran in lexical-only "
                        "mode. Local embeddings can be added later without changing the interface."
                    ),
                    claim_id=claim.claim_id,
                )
            )

        ordered_chunk_indexes = [
            chunk_index
            for chunk_index, _score in sorted(
                fused_scores.items(),
                key=lambda item: (item[1], lexical_scores[item[0]]),
                reverse=True,
            )
        ]

        if not ordered_chunk_indexes and lexical_ranks:
            ordered_chunk_indexes = lexical_ranks

        evidence: list[EvidenceCandidate] = []
        for rank, chunk_index in enumerate(ordered_chunk_indexes[:limit], start=1):
            chunk = self.chunks[chunk_index]
            semantic_score = semantic_scores[chunk_index] if semantic_scores is not None else None
            evidence.append(
                EvidenceCandidate(
                    evidence_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    source_path=chunk.source_path,
                    snippet=chunk.text,
                    page_number=chunk.page_number,
                    section=chunk.section,
                    block_kind=chunk.block_kind,
                    retrieval_rank=rank,
                    fused_score=fused_scores.get(chunk_index, 0.0),
                    lexical_score=lexical_scores[chunk_index],
                    semantic_score=semantic_score,
                    metadata={
                        "index_text": chunk.index_text,
                        "block_id": chunk.metadata.get("block_id"),
                        "extractor": chunk.metadata.get("extractor"),
                    },
                )
            )

        if not evidence:
            findings.append(
                RetrievalFinding(
                    code="retrieval-no-evidence",
                    severity="warning",
                    message="TRACE could not retrieve evidence candidates for this claim.",
                    claim_id=claim.claim_id,
                )
            )

        return RetrievalResult(
            claim=claim,
            evidence=evidence,
            findings=findings,
            metadata={
                "chunk_count": len(self.chunks),
                "lexical_rank_count": len(lexical_ranks),
                "semantic_rank_count": len(semantic_ranks),
                "semantic_enabled": semantic_scores is not None,
            },
        )

    def retrieve_many(self, claims: Iterable[Claim], top_k: int | None = None) -> list[RetrievalResult]:
        """Retrieve evidence for multiple claims."""

        return [self.retrieve(claim, top_k=top_k) for claim in claims]
