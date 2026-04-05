"""Evidence retrieval stage."""

from __future__ import annotations

from trace_core.schemas import Claim, EvidenceSpan, SourceDocument


def retrieve_evidence(claim: Claim, documents: list[SourceDocument], top_k: int = 3) -> list[EvidenceSpan]:
    """Return placeholder evidence candidates for a claim.

    The current implementation returns the first available document snippets.
    It provides a stable interface for later replacement with hybrid semantic
    and lexical retrieval.
    """
    evidence: list[EvidenceSpan] = []

    for document in documents[:top_k]:
        snippet = document.text.strip()[:280]
        evidence.append(
            EvidenceSpan(
                document_id=document.document_id,
                snippet=snippet,
                section=document.section,
                score=None,
            )
        )

    return evidence
