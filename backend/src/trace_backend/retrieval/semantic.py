"""Optional local embedding support for TRACE retrieval."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Protocol
from urllib import request

import numpy as np


class EmbeddingProvider(Protocol):
    """Protocol for an embedding backend."""

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Return one embedding vector per input string."""


@dataclass(slots=True)
class OpenAICompatibleEmbeddingProvider:
    """Embedding provider backed by a local OpenAI-compatible endpoint."""

    base_url: str
    model: str
    api_key: str | None = None
    timeout_seconds: float = 30.0

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=float)

        endpoint = self.base_url.rstrip("/") + "/embeddings"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = json.dumps({"model": self.model, "input": texts}).encode("utf-8")
        http_request = request.Request(endpoint, data=payload, headers=headers, method="POST")

        with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))

        data = body.get("data", [])
        vectors = [item.get("embedding", []) for item in data]
        return np.array(vectors, dtype=float)

    @classmethod
    def from_env(cls, prefix: str = "TRACE_EMBED") -> "OpenAICompatibleEmbeddingProvider | None":
        """Build an embedding provider from environment variables."""

        base_url = os.getenv(f"{prefix}_BASE_URL")
        model = os.getenv(f"{prefix}_MODEL")
        if not base_url or not model:
            return None

        return cls(
            base_url=base_url,
            model=model,
            api_key=os.getenv(f"{prefix}_API_KEY"),
            timeout_seconds=float(os.getenv(f"{prefix}_TIMEOUT", "30")),
        )


def cosine_similarity_matrix(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return cosine similarity between two embedding matrices."""

    if left.size == 0 or right.size == 0:
        return np.zeros((left.shape[0], right.shape[0]), dtype=float)

    left_norm = left / np.clip(np.linalg.norm(left, axis=1, keepdims=True), a_min=1e-12, a_max=None)
    right_norm = right / np.clip(np.linalg.norm(right, axis=1, keepdims=True), a_min=1e-12, a_max=None)
    return left_norm @ right_norm.T
