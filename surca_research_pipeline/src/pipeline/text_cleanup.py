from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, List


POINTS_MARKERS = [
    "POINTS TO CONSIDER",
    "POINTS THAT MUST BE CONSIDERED",
    "POINTS TO CONSIDER (continued)",
]

TEMPLATE_ONLY_PATTERNS = [
    r"^the parent and the school district have agreed that this student requires advanced educational planning",
    r"^the district has procedures for notifying parents regarding the use of restraint or isolation",
    r"^form 6[dh]\b",
    r"^behavioral intervention plan \(bip\) by office of superintendent",
    r"^(a \|\| )?use large print\b",
    r"^audio digital books\b",
    r"^(a \|\| )?alter format of materials\b",
    r"^provide study outlines/guides/graphic organizers\b",
    r"^cloze reading strategy\b",
    r"^read class materials orally\b",
    r"^low-vision devices\b",
    r"^sign language\b",
    r"^shortened assignments\b",
    r"^limited multiple choice\b",
    r"^modify/repeat/model directions\b",
    r"^(a \|\| )?rephrase test questions\b",
    r"^provide test/assessment study guide\b",
    r"^provide extra credit options\b",
    r"^(a \|\| )?simplify text wording/language\b",
    r"^assign peer tutor/note taker\b",
    r"^prior notice of assignments/assessments\b",
    r"^modify student.?s schedule\b",
]

INLINE_TEMPLATE_SEGMENTS = [
    r"If yes, consider the student.?s need for positive behavioral supports/ interventions, a Functional Behavioral Assessment \(FBA\), and/or a Behavioral Intervention Plan \(BIP\)\.",
]


@dataclass
class RemovedText:
    reason: str
    text: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


def _compact_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _strip_template_side(line: str) -> tuple[str, List[RemovedText]]:
    kept = line
    removed: List[RemovedText] = []

    for pattern in INLINE_TEMPLATE_SEGMENTS:
        match = re.search(pattern, kept)
        if match:
            removed.append(RemovedText("inline_template_guidance", match.group(0)))
            kept = re.sub(pattern, "", kept)

    marker_positions = []
    upper_line = kept.upper()
    for marker in POINTS_MARKERS:
        index = upper_line.find(marker)
        if index >= 0:
            marker_positions.append(index)

    if not marker_positions:
        return kept, removed

    cut_at = min(marker_positions)
    before = kept[:cut_at].rstrip(" |")
    after = kept[cut_at:].strip()

    if after:
        removed.append(RemovedText("template_points_to_consider", after))

    return before, removed


def clean_extracted_text_for_model(text: str) -> Dict[str, object]:
    """Remove obvious form boilerplate while keeping student-specific text visible."""
    raw_lines = [line.strip() for line in (text or "").splitlines()]
    cleaned_lines: List[str] = []
    removed: List[RemovedText] = []
    seen_clean_lines = set()

    for line in raw_lines:
        compact = _compact_spaces(line)
        if not compact:
            continue

        lowered = compact.lower()
        if any(re.search(pattern, lowered) for pattern in TEMPLATE_ONLY_PATTERNS):
            removed.append(RemovedText("template_only_line", compact))
            continue

        kept, removed_from_line = _strip_template_side(compact)
        removed.extend(removed_from_line)
        kept = _compact_spaces(kept)

        if not kept:
            continue

        # Deduping is line-level only. It does not remove facts that appear once.
        dedupe_key = kept.lower()
        if dedupe_key in seen_clean_lines:
            removed.append(RemovedText("duplicate_extracted_line", kept))
            continue

        seen_clean_lines.add(dedupe_key)
        cleaned_lines.append(kept)

    cleaned_text = "\n".join(cleaned_lines).strip()
    removed_rows = [item.to_dict() for item in removed]
    removed_by_reason: Dict[str, int] = {}
    for item in removed_rows:
        reason = item["reason"]
        removed_by_reason[reason] = removed_by_reason.get(reason, 0) + 1

    return {
        "cleaned_text": cleaned_text,
        "audit": {
            "raw_line_count": len([line for line in raw_lines if line.strip()]),
            "cleaned_line_count": len(cleaned_lines),
            "raw_char_count": len(text or ""),
            "cleaned_char_count": len(cleaned_text),
            "removed_count": len(removed_rows),
            "removed_by_reason": dict(sorted(removed_by_reason.items())),
            "removed_examples": removed_rows[:25],
        },
    }
