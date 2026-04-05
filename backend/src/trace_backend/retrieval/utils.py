"""Utility helpers for TRACE retrieval."""

from __future__ import annotations

import re
from typing import Iterable

WHITESPACE_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'/-]*")
BIGRAM_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'/-]*")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


def normalize_text(text: str) -> str:
    """Normalize retrieval text by collapsing whitespace."""

    return WHITESPACE_RE.sub(" ", text or "").strip()


def tokenize(text: str) -> list[str]:
    """Tokenize a string for lexical retrieval."""

    return [token.lower() for token in TOKEN_RE.findall(text)]


def bigrams(text: str) -> set[str]:
    """Return lowercased token bigrams."""

    tokens = [token.lower() for token in BIGRAM_RE.findall(text)]
    return {
        f"{tokens[index]} {tokens[index + 1]}"
        for index in range(len(tokens) - 1)
    }


def extract_numbers(text: str) -> set[str]:
    """Return normalized number-like tokens."""

    return set(NUMBER_RE.findall(text or ""))


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    """Return a list with duplicates removed while preserving order."""

    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped
