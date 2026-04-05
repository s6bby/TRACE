"""Heuristics and text utilities for TRACE claim extraction."""

from __future__ import annotations

from dataclasses import dataclass
import re

from trace_backend.claims.models import ClaimExtractionConfig, TextSpan

WHITESPACE_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'/-]*")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*•]|(?:\d+|[A-Za-z])[\.\)])\s+")
COMMON_ABBREVIATIONS = {
    "mr.",
    "mrs.",
    "ms.",
    "dr.",
    "prof.",
    "sr.",
    "jr.",
    "st.",
    "vs.",
    "etc.",
    "e.g.",
    "i.e.",
    "u.s.",
    "fig.",
    "no.",
}
COMMON_VERBS = {
    "is",
    "are",
    "was",
    "were",
    "be",
    "being",
    "been",
    "has",
    "have",
    "had",
    "does",
    "do",
    "did",
    "can",
    "could",
    "should",
    "must",
    "may",
    "might",
    "will",
    "would",
    "receives",
    "receive",
    "received",
    "requires",
    "require",
    "required",
    "needs",
    "need",
    "needed",
    "provides",
    "provide",
    "provided",
    "includes",
    "include",
    "included",
    "recommends",
    "recommend",
    "recommended",
    "shows",
    "show",
    "showed",
    "states",
    "state",
    "stated",
    "lists",
    "list",
    "listed",
    "identifies",
    "identify",
    "identified",
    "supports",
    "support",
    "supported",
}
TITLECASE_CONNECTORS = {"and", "or", "but", "for", "nor", "so", "yet", "to", "of", "in", "on", "at"}
CONDITIONAL_MARKERS = {"if", "when", "whenever", "unless", "until", "provided", "assuming"}
REFERENTIAL_MARKERS = {"this", "that", "these", "those", "it", "they", "them", "he", "she"}
ENUMERATION_INTRODUCER_RE = re.compile(
    r"^(?P<prefix>.*?\b(?:include(?:s|d)?|provide(?:s|d)?|offer(?:s|ed)?|receive(?:s|d)?|"
    r"recommend(?:s|ed)?|list(?:s|ed)?|identify(?:ies|ied)?|describe(?:s|d)?|mention(?:s|ed)?)\b)\s+"
    r"(?P<items>.+)$",
    re.IGNORECASE,
)


@dataclass(slots=True)
class ResponseBlock:
    """A logical block in the raw model response."""

    span: TextSpan
    block_kind: str


def normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace."""

    return WHITESPACE_RE.sub(" ", text or "").strip()


def normalize_claim_text(text: str) -> str:
    """Normalize a claim candidate without losing the original source span."""

    cleaned = LIST_ITEM_RE.sub("", text or "").strip()
    return normalize_whitespace(cleaned)


def sentence_case(text: str) -> str:
    """Uppercase the first alphabetical character for display."""

    if not text:
        return text

    for index, char in enumerate(text):
        if char.isalpha():
            return text[:index] + char.upper() + text[index + 1 :]
    return text


def tokenize(text: str) -> list[str]:
    """Return conservative alphanumeric tokens."""

    return TOKEN_RE.findall(text)


def is_list_item(text: str) -> bool:
    """Return whether the raw text resembles a list item."""

    return bool(LIST_ITEM_RE.match(text or ""))


def strip_list_marker(text: str) -> str:
    """Remove a leading list marker from a line."""

    return LIST_ITEM_RE.sub("", text or "", count=1)


def contains_likely_verb(text: str) -> bool:
    """Approximate whether the text contains a verbal predicate."""

    tokens = [token.lower() for token in tokenize(text)]
    if any(token in COMMON_VERBS for token in tokens):
        return True

    return any(
        len(token) > 4 and token.endswith(("ed", "ing"))
        for token in tokens
    )


def is_heading_like(text: str, config: ClaimExtractionConfig) -> bool:
    """Return whether a block looks more like a heading than a claim."""

    normalized = normalize_claim_text(text)
    if not normalized:
        return False

    if normalized.endswith((".", "!", "?")):
        return False

    tokens = tokenize(normalized)
    if not tokens or len(tokens) > config.max_heading_tokens:
        return False

    if contains_likely_verb(normalized):
        return False

    if normalized.endswith(":"):
        return True

    if normalized.isupper():
        return True

    titled = normalized.split()
    if titled and all(
        word[:1].isupper() or word.lower() in TITLECASE_CONNECTORS or word.isdigit()
        for word in titled
    ):
        return True

    return False


def iter_response_blocks(response_text: str) -> list[ResponseBlock]:
    """Group the raw response into logical paragraph and list blocks."""

    blocks: list[ResponseBlock] = []
    current_start: int | None = None
    current_end: int | None = None

    offset = 0
    for line in response_text.splitlines(keepends=True):
        line_body = line.rstrip("\r\n")
        line_start = offset
        line_end = offset + len(line_body)
        offset += len(line)

        if not line_body.strip():
            if current_start is not None and current_end is not None:
                raw_block = response_text[current_start:current_end]
                blocks.append(
                    ResponseBlock(
                        span=TextSpan(current_start, current_end, raw_block),
                        block_kind="paragraph",
                    )
                )
                current_start = None
                current_end = None
            continue

        if is_list_item(line_body):
            if current_start is not None and current_end is not None:
                raw_block = response_text[current_start:current_end]
                blocks.append(
                    ResponseBlock(
                        span=TextSpan(current_start, current_end, raw_block),
                        block_kind="paragraph",
                    )
                )
                current_start = None
                current_end = None

            blocks.append(
                ResponseBlock(
                    span=TextSpan(line_start, line_end, response_text[line_start:line_end]),
                    block_kind="list_item",
                )
            )
            continue

        if current_start is None:
            current_start = line_start
        current_end = line_end

    if current_start is not None and current_end is not None:
        raw_block = response_text[current_start:current_end]
        blocks.append(
            ResponseBlock(
                span=TextSpan(current_start, current_end, raw_block),
                block_kind="paragraph",
            )
        )

    return blocks


def _last_token_before(text: str, index: int) -> str:
    token = re.search(r"([A-Za-z][A-Za-z.]*)$", text[: index + 1])
    return token.group(1).lower() if token else ""


def _is_sentence_boundary(raw_text: str, index: int, config: ClaimExtractionConfig) -> bool:
    char = raw_text[index]
    if char == ";":
        return config.split_on_semicolons

    if char not in ".?!":
        return False

    if char == ".":
        if index > 0 and raw_text[index - 1] == ".":
            return False
        if index + 1 < len(raw_text) and raw_text[index + 1] == ".":
            return False
        if index > 0 and index + 1 < len(raw_text):
            if raw_text[index - 1].isdigit() and raw_text[index + 1].isdigit():
                return False

    token = _last_token_before(raw_text, index)
    if token in COMMON_ABBREVIATIONS:
        return False

    if len(token) == 2 and token.endswith(".") and token[0].isalpha():
        next_slice = raw_text[index + 1 :]
        next_match = re.search(r"\S", next_slice)
        if next_match and next_slice[next_match.start()].isupper():
            return False

    return True


def split_sentences(span: TextSpan, config: ClaimExtractionConfig) -> list[TextSpan]:
    """Split a block into sentence-like spans while preserving offsets."""

    raw = span.text
    sentences: list[TextSpan] = []
    sentence_start = 0
    index = 0

    while index < len(raw):
        if _is_sentence_boundary(raw, index, config):
            sentence_end = index + 1
            while sentence_end < len(raw) and raw[sentence_end] in "\"')]} ":
                sentence_end += 1

            candidate = raw[sentence_start:sentence_end]
            if candidate.strip():
                sentences.append(
                    TextSpan(
                        span.start_char + sentence_start,
                        span.start_char + sentence_end,
                        candidate,
                    )
                )
            sentence_start = sentence_end
            index = sentence_end
            continue

        index += 1

    tail = raw[sentence_start:]
    if tail.strip():
        sentences.append(
            TextSpan(
                span.start_char + sentence_start,
                span.end_char,
                tail,
            )
        )

    return sentences


def starts_with_referential_marker(text: str) -> bool:
    """Return whether the claim begins with a context-dependent pronoun."""

    tokens = tokenize(text.lower())
    return bool(tokens and tokens[0] in REFERENTIAL_MARKERS)


def contains_conditional_marker(text: str) -> bool:
    """Return whether the claim contains a conditional marker."""

    tokens = {token.lower() for token in tokenize(text)}
    return any(marker in tokens for marker in CONDITIONAL_MARKERS)


def suggest_connector_split(text: str) -> list[str]:
    """Suggest separate claims for contrastive compound statements."""

    normalized = normalize_claim_text(text)
    lowered = f" {normalized.lower()} "

    for connector in (" but ", " however ", " whereas ", " although ", " while "):
        if connector not in lowered:
            continue

        left, right = re.split(connector.strip(), normalized, maxsplit=1, flags=re.IGNORECASE)
        left = normalize_whitespace(left).rstrip(",;:")
        right = normalize_whitespace(right).lstrip(",;:")
        if left and right and contains_likely_verb(left) and contains_likely_verb(right):
            return [sentence_case(left.rstrip(".") + "."), sentence_case(right.rstrip(".") + ".")]

    return []


def suggest_enumeration_splits(text: str, max_splits: int) -> list[str]:
    """Suggest separate claims for list-like statements when the split is reasonably safe."""

    normalized = normalize_claim_text(text)
    match = ENUMERATION_INTRODUCER_RE.match(normalized)
    if match is None:
        return []

    prefix = normalize_whitespace(match.group("prefix"))
    items_text = normalize_whitespace(match.group("items").rstrip("."))
    if "," not in items_text:
        return []

    items = [
        normalize_whitespace(re.sub(r"^(?:and|or)\s+", "", item, flags=re.IGNORECASE))
        for item in re.split(r",\s*|\s+(?:and|or)\s+", items_text)
        if normalize_whitespace(item)
    ]
    if len(items) < 2:
        return []

    suggestions = [f"{prefix} {item}." for item in items[:max_splits]]
    deduped: list[str] = []
    for suggestion in suggestions:
        if suggestion not in deduped:
            deduped.append(suggestion)
    return deduped
