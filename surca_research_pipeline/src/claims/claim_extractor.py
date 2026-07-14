from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional


BULLET_PREFIX_RE = re.compile(r"^\s*(?:[-*•]+|\d+[.)])\s*")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")

# These patterns are intentionally broad. The first prototype should favor
# capturing checkable statements over perfect precision.
CLAIM_SIGNAL_PATTERNS = [
    r"\b(student|iep|bip|fba|documentation|documents)\b",
    r"\b(aggression|behavior|transition|elopement|self[- ]injury|task refusal|yelling|screaming)\b",
    r"\b(ot|speech|service|services|accommodation|schedule|break card|support|supervision|ratio)\b",
    r"\b(escape|attention|tangible|sensory|safety|restraint|isolation)\b",
    r"\b(receives?|shows?|exhibits?|uses?|includes?|requires?|needs?|occurs?|lasts?|appears?|recommended?|recommend)\b",
    r"\b(cannot determine|not specified|not stated|not documented|not included|insufficient information)\b",
    r"\b\d+\s*(times?|minutes?|hours?|x|:1)\b",
]

NON_CLAIM_PATTERNS = [
    r"^here (are|is)\b",
    r"^overall\b",
    r"^in summary\b",
    r"^please\b",
    r"^thank you\b",
    r"^this is important to remember\b",
]

CLAIM_TYPE_RULES: Dict[str, List[str]] = {
    "function": [
        r"\b(escape|attention|tangible|sensory|function|maintained by)\b",
    ],
    "service": [
        r"\b(ot|speech|service|services|bip|fba)\b",
    ],
    "accommodation": [
        r"\b(visual schedule|break card|accommodation|timer|visual support|graphic organizer)\b",
    ],
    "safety": [
        r"\b(safety|restraint|isolation|crisis|unsafe)\b",
    ],
    "staffing_or_support": [
        r"\b(1:1|2:1|supervision|support level|staffing|closer supervision)\b",
    ],
    "recommendation": [
        r"\b(recommend|should|would be appropriate|would be needed|may need)\b",
    ],
    "behavior": [
        r"\b(aggression|aggressive|yelling|screaming|elopement|task refusal|self[- ]injury|behavior)\b",
    ],
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "based",
    "be",
    "by",
    "can",
    "does",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "student",
    "the",
    "this",
    "to",
    "with",
}

ABSTENTION_WORDS_RE = re.compile(
    r"\b(cannot determine|not specified|not stated|not documented|not included|unclear|unknown)\b"
)


@dataclass
class Claim:
    claim_id: str
    source_text: str
    normalized_text: str
    claim_type: str
    source_unit_index: int
    support_status: str = "not_checked"
    support_reason: str = "document evidence check was not run"
    support_evidence: str = ""
    support_score: float = 0.0

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class ClaimUnit:
    unit_index: int
    source_text: str
    normalized_text: str
    looks_like_claim: bool
    claim_type: Optional[str] = None
    claim_id: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def normalize_claim_text(text: str) -> str:
    value = unicodedata.normalize("NFKC", text or "")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = value.replace("\u2022", "\n- ")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _split_paragraph_into_units(paragraph: str) -> List[str]:
    stripped = paragraph.strip()
    if not stripped:
        return []

    bullet_candidate = BULLET_PREFIX_RE.sub("", stripped)
    if bullet_candidate != stripped:
        return [bullet_candidate.strip()] if bullet_candidate.strip() else []

    parts = [part.strip() for part in SENTENCE_SPLIT_RE.split(stripped) if part.strip()]
    if len(parts) > 1:
        return parts
    return [stripped]


def split_candidate_units(raw_response: str) -> List[str]:
    text = normalize_claim_text(raw_response)
    if not text:
        return []

    units: List[str] = []
    for paragraph in text.split("\n\n"):
        for line in paragraph.split("\n"):
            units.extend(_split_paragraph_into_units(line))

    cleaned: List[str] = []
    seen = set()
    for unit in units:
        normalized = re.sub(r"\s+", " ", unit).strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            cleaned.append(normalized)
    return cleaned


def looks_like_claim(unit: str) -> bool:
    text = normalize_claim_text(unit)
    if not text:
        return False

    lowered = text.lower()
    if len(lowered.split()) < 4:
        return False

    if any(re.search(pattern, lowered) for pattern in NON_CLAIM_PATTERNS):
        return False

    return any(re.search(pattern, lowered) for pattern in CLAIM_SIGNAL_PATTERNS)


def classify_claim_type(unit: str) -> str:
    lowered = normalize_claim_text(unit).lower()
    for claim_type, patterns in CLAIM_TYPE_RULES.items():
        if any(re.search(pattern, lowered) for pattern in patterns):
            return claim_type
    return "other"


def summarize_claim_types(claims: List[Dict[str, object]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for claim in claims:
        claim_type = str(claim.get("claim_type", "other"))
        counts[claim_type] = counts.get(claim_type, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[0]))


def _keywords(text: str) -> List[str]:
    words = re.findall(r"[a-z0-9][a-z0-9:-]{2,}", normalize_claim_text(text).lower())
    cleaned = []
    seen = set()
    for word in words:
        if word in STOP_WORDS:
            continue
        if word.endswith("s") and len(word) > 4:
            word = word[:-1]
        if word not in seen:
            seen.add(word)
            cleaned.append(word)
    return cleaned


def _source_units(document_text: str) -> List[str]:
    units = []
    for line in normalize_claim_text(document_text).splitlines():
        line = line.strip()
        if not line:
            continue
        parts = re.split(r"\s+\|\|\s+|\s+\|\s+", line)
        for part in parts:
            part = part.strip()
            if len(part.split()) >= 3:
                units.append(part)
    return units


def check_claim_support(claim_text: str, document_text: str) -> Dict[str, object]:
    claim = normalize_claim_text(claim_text)
    source = normalize_claim_text(document_text)
    lowered_claim = claim.lower()

    if not claim:
        return {
            "support_status": "unclear",
            "support_reason": "empty claim",
            "support_evidence": "",
            "support_score": 0.0,
        }

    if ABSTENTION_WORDS_RE.search(lowered_claim):
        return {
            "support_status": "unclear",
            "support_reason": "claim says the document does not specify something",
            "support_evidence": "",
            "support_score": 0.0,
        }

    if lowered_claim in source.lower():
        return {
            "support_status": "supported",
            "support_reason": "exact text appears in cleaned document text",
            "support_evidence": claim,
            "support_score": 1.0,
        }

    claim_words = _keywords(claim)
    if not claim_words:
        return {
            "support_status": "unclear",
            "support_reason": "not enough claim keywords to check",
            "support_evidence": "",
            "support_score": 0.0,
        }

    best_unit = ""
    best_score = 0.0
    best_overlap_count = 0

    for unit in _source_units(source):
        unit_words = set(_keywords(unit))
        if not unit_words:
            continue
        overlap_count = sum(1 for word in claim_words if word in unit_words)
        score = overlap_count / max(len(claim_words), 1)
        if score > best_score:
            best_score = score
            best_overlap_count = overlap_count
            best_unit = unit

    if best_score >= 0.55 and best_overlap_count >= 3:
        status = "supported"
        reason = "enough claim keywords match one source text unit"
    elif best_score >= 0.30 and best_overlap_count >= 2:
        status = "unclear"
        reason = "some source keywords match, but not enough for a clean support call"
    else:
        status = "unsupported"
        reason = "no close source text match found"

    return {
        "support_status": status,
        "support_reason": reason,
        "support_evidence": best_unit,
        "support_score": round(best_score, 3),
    }


def build_claim_breakdown(raw_response: str, prefix: str = "claim", document_text: str = "") -> Dict[str, object]:
    units = split_candidate_units(raw_response)
    claims: List[Dict[str, object]] = []
    unit_rows: List[Dict[str, object]] = []

    kept_count = 0
    for index, unit in enumerate(units, start=1):
        kept = looks_like_claim(unit)
        claim_type = None
        claim_id = None

        if kept:
            kept_count += 1
            claim_id = f"{prefix}_{kept_count:03d}"
            claim_type = classify_claim_type(unit)
            support = (
                check_claim_support(unit, document_text)
                if document_text
                else {
                    "support_status": "not_checked",
                    "support_reason": "document text was not provided",
                    "support_evidence": "",
                    "support_score": 0.0,
                }
            )
            claims.append(
                Claim(
                    claim_id=claim_id,
                    source_text=unit,
                    normalized_text=normalize_claim_text(unit).lower(),
                    claim_type=claim_type,
                    source_unit_index=index,
                    **support,
                ).to_dict()
            )

        unit_rows.append(
            ClaimUnit(
                unit_index=index,
                source_text=unit,
                normalized_text=normalize_claim_text(unit).lower(),
                looks_like_claim=kept,
                claim_type=claim_type,
                claim_id=claim_id,
            ).to_dict()
        )

    support_counts: Dict[str, int] = {}
    for claim in claims:
        status = str(claim.get("support_status", "not_checked"))
        support_counts[status] = support_counts.get(status, 0) + 1

    return {
        "source_unit_count": len(units),
        "claim_count": len(claims),
        "claims_by_type": summarize_claim_types(claims),
        "claim_support_counts": dict(sorted(support_counts.items())),
        "units": unit_rows,
        "claims": claims,
    }


def extract_claims(raw_response: str, prefix: str = "claim", document_text: str = "") -> List[Dict[str, object]]:
    return build_claim_breakdown(raw_response, prefix, document_text=document_text)["claims"]
