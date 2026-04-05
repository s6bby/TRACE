"""Multi-judge evaluation orchestration for TRACE."""

from __future__ import annotations

from collections import Counter
from statistics import mean

from trace_backend.claims.models import Claim
from trace_backend.evaluation.heuristic import heuristic_judge_decision
from trace_backend.evaluation.llm import OpenAICompatibleJudge, load_local_judges_from_env, run_judges_parallel
from trace_backend.evaluation.models import EvaluationConfig
from trace_backend.evaluation.validation import validate_judge_decision
from trace_backend.pipeline.models import (
    ClaimAssessment,
    EvidenceCandidate,
    JudgeDecision,
    ValidationFinding,
)

LABEL_TO_SCORE = {"unsupported": 0, "inferred": 1, "explicit": 2}
SCORE_TO_LABEL = {value: key for key, value in LABEL_TO_SCORE.items()}


def _normalize_label(label: str) -> str:
    label = (label or "").strip().lower()
    if label not in LABEL_TO_SCORE:
        return "unsupported"
    return label


def _normalize_priority(priority: str) -> str:
    priority = (priority or "").strip().lower()
    if priority not in {"low", "normal", "high"}:
        return "normal"
    return priority


def _resolve_contested_label(decisions: list[JudgeDecision]) -> str:
    scores = [LABEL_TO_SCORE[_normalize_label(decision.label)] for decision in decisions]
    resolved_score = round(mean(scores))
    return SCORE_TO_LABEL[int(resolved_score)]


def _consensus_citations(decisions: list[JudgeDecision]) -> list[str]:
    counter: Counter[str] = Counter()
    for decision in decisions:
        counter.update(decision.cited_evidence_ids)
    return [
        evidence_id
        for evidence_id, count in counter.most_common()
        if count >= 2
    ]


class MultiJudgeEvaluator:
    """Evaluate claims with optional local LLM judges plus deterministic checks."""

    def __init__(
        self,
        config: EvaluationConfig | None = None,
        judges: list[OpenAICompatibleJudge] | None = None,
        adjudicator: OpenAICompatibleJudge | None = None,
    ) -> None:
        self.config = config or EvaluationConfig()
        if judges is None and adjudicator is None:
            loaded_judges, loaded_adjudicator = load_local_judges_from_env()
            self.judges = loaded_judges
            self.adjudicator = loaded_adjudicator
        else:
            self.judges = judges or []
            self.adjudicator = adjudicator

    def _validated_decision(
        self,
        claim: Claim,
        evidence: list[EvidenceCandidate],
        decision: JudgeDecision,
    ) -> tuple[JudgeDecision, list[ValidationFinding]]:
        normalized = JudgeDecision(
            judge_id=decision.judge_id,
            label=_normalize_label(decision.label),  # type: ignore[arg-type]
            cited_evidence_ids=decision.cited_evidence_ids,
            rationale=decision.rationale,
            ambiguity_note=decision.ambiguity_note,
            review_priority=_normalize_priority(decision.review_priority),  # type: ignore[arg-type]
            metadata=decision.metadata,
        )
        findings = validate_judge_decision(claim, normalized, evidence)
        return normalized, findings

    def evaluate(self, claim: Claim, evidence: list[EvidenceCandidate]) -> ClaimAssessment:
        """Return one TRACE assessment for a claim and its evidence candidates."""

        if not self.judges:
            heuristic = heuristic_judge_decision(claim, evidence[: self.config.top_k_evidence])
            validated, findings = self._validated_decision(claim, evidence, heuristic)
            return ClaimAssessment(
                claim=claim,
                label=validated.label,
                evidence=evidence[: self.config.top_k_evidence],
                cited_evidence_ids=validated.cited_evidence_ids,
                note=validated.rationale,
                review_priority="high" if claim.ambiguous else validated.review_priority,
                agreement_status="heuristic",
                judge_decisions=[validated],
                validation_findings=findings,
                metadata={"evaluation_mode": "heuristic"},
            )

        judge_decisions = run_judges_parallel(self.judges, claim, evidence[: self.config.top_k_evidence])
        normalized_decisions: list[JudgeDecision] = []
        validation_findings: list[ValidationFinding] = []

        for decision in judge_decisions:
            normalized, findings = self._validated_decision(claim, evidence, decision)
            normalized_decisions.append(normalized)
            validation_findings.extend(findings)

        labels = [decision.label for decision in normalized_decisions]
        label_counts = Counter(labels)
        most_common_label, most_common_count = label_counts.most_common(1)[0]

        if len(normalized_decisions) == 1:
            final_label = most_common_label
            agreement_status = "single_judge"
            cited_evidence_ids = normalized_decisions[0].cited_evidence_ids
            note = normalized_decisions[0].rationale
            priority = normalized_decisions[0].review_priority
        elif most_common_count == len(normalized_decisions):
            final_label = most_common_label
            agreement_status = "consensus"
            cited_evidence_ids = _consensus_citations(normalized_decisions) or normalized_decisions[0].cited_evidence_ids
            note = "All configured judges agreed on the provisional support label."
            priority = "normal"
        elif self.adjudicator is not None:
            adjudicated = self.adjudicator.adjudicate_claim(
                claim,
                evidence[: self.config.top_k_evidence],
                normalized_decisions,
            )
            normalized_adjudicated, adjudication_findings = self._validated_decision(claim, evidence, adjudicated)
            normalized_decisions.append(normalized_adjudicated)
            validation_findings.extend(adjudication_findings)
            final_label = normalized_adjudicated.label
            agreement_status = "adjudicated"
            cited_evidence_ids = normalized_adjudicated.cited_evidence_ids
            note = normalized_adjudicated.rationale
            priority = normalized_adjudicated.review_priority
        else:
            final_label = _resolve_contested_label(normalized_decisions)
            agreement_status = "contested"
            cited_evidence_ids = _consensus_citations(normalized_decisions)
            note = (
                "Configured judges disagreed on the claim label. TRACE used a conservative "
                "midpoint resolution and elevated the claim for review."
            )
            priority = "high"

        if claim.ambiguous and self.config.high_priority_on_ambiguity:
            priority = "high"
        if agreement_status == "contested" and self.config.high_priority_on_contested_label:
            priority = "high"
        if any(finding.severity == "error" for finding in validation_findings):
            priority = "high"

        evidence_map = {item.evidence_id: item for item in evidence}
        cited_evidence = [
            evidence_map[evidence_id]
            for evidence_id in cited_evidence_ids
            if evidence_id in evidence_map
        ]

        return ClaimAssessment(
            claim=claim,
            label=final_label,  # type: ignore[arg-type]
            evidence=cited_evidence or evidence[: self.config.top_k_evidence],
            cited_evidence_ids=cited_evidence_ids,
            note=note,
            review_priority=priority,  # type: ignore[arg-type]
            agreement_status=agreement_status,  # type: ignore[arg-type]
            judge_decisions=normalized_decisions,
            validation_findings=validation_findings,
            metadata={"evaluation_mode": "local_llm" if self.judges else "heuristic"},
        )
