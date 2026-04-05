"""Lexical scoring for TRACE evidence retrieval."""

from __future__ import annotations

from collections import Counter
import math

from trace_backend.claims.models import Claim
from trace_backend.retrieval.models import RetrievalChunk
from trace_backend.retrieval.utils import bigrams, extract_numbers, tokenize


class LexicalScorer:
    """BM25-style lexical retrieval with claim-aware bonuses."""

    def __init__(self, chunks: list[RetrievalChunk]) -> None:
        self._chunks = chunks
        self._chunk_tokens = [tokenize(chunk.index_text) for chunk in chunks]
        self._chunk_bigrams = [bigrams(chunk.index_text) for chunk in chunks]
        self._chunk_numbers = [extract_numbers(chunk.index_text) for chunk in chunks]
        self._avg_doc_len = (
            sum(len(tokens) for tokens in self._chunk_tokens) / len(self._chunk_tokens)
            if self._chunk_tokens
            else 0.0
        )
        self._idf = self._build_idf()
        self._k1 = 1.2
        self._b = 0.75

    def _build_idf(self) -> dict[str, float]:
        doc_count = len(self._chunk_tokens)
        document_frequency: Counter[str] = Counter()

        for tokens in self._chunk_tokens:
            for token in set(tokens):
                document_frequency[token] += 1

        return {
            token: math.log(1.0 + (doc_count - freq + 0.5) / (freq + 0.5))
            for token, freq in document_frequency.items()
        }

    def score(self, claim: Claim, chunk: RetrievalChunk, chunk_index: int) -> float:
        """Return a lexical relevance score for one chunk."""

        query_tokens = tokenize(claim.text)
        if not query_tokens:
            return 0.0

        doc_tokens = self._chunk_tokens[chunk_index]
        doc_counter = Counter(doc_tokens)
        doc_len = len(doc_tokens) or 1

        bm25 = 0.0
        for token in query_tokens:
            if token not in doc_counter:
                continue
            idf = self._idf.get(token, 0.0)
            tf = doc_counter[token]
            denom = tf + self._k1 * (1.0 - self._b + self._b * doc_len / (self._avg_doc_len or 1.0))
            bm25 += idf * ((tf * (self._k1 + 1.0)) / denom)

        query_bigrams = bigrams(claim.text)
        shared_bigrams = len(query_bigrams & self._chunk_bigrams[chunk_index])
        if query_bigrams:
            bm25 += 0.35 * (shared_bigrams / len(query_bigrams))

        claim_numbers = extract_numbers(claim.text)
        shared_numbers = len(claim_numbers & self._chunk_numbers[chunk_index])
        if claim_numbers:
            bm25 += 0.4 * (shared_numbers / len(claim_numbers))

        if chunk.section:
            section_tokens = set(tokenize(chunk.section))
            query_token_set = set(query_tokens)
            if section_tokens & query_token_set:
                bm25 += 0.15

        if chunk.block_kind == "table" and claim_numbers:
            bm25 += 0.1

        return bm25
