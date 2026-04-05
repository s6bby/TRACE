from __future__ import annotations

from pathlib import Path

from trace_backend.claims.models import Claim, TextSpan
from trace_backend.evaluation import EvaluationConfig, MultiJudgeEvaluator
from trace_backend.pipeline import EvidenceCandidate


class FakeJudge:
    def __init__(self, judge_id: str, label: str, cited_evidence_ids: list[str], rationale: str) -> None:
        self.judge_id = judge_id
        self._label = label
        self._cited_evidence_ids = cited_evidence_ids
        self._rationale = rationale

    def evaluate_claim(self, claim: Claim, evidence: list[EvidenceCandidate]):
        del claim, evidence
        from trace_backend.pipeline.models import JudgeDecision

        return JudgeDecision(
            judge_id=self.judge_id,
            label=self._label,  # type: ignore[arg-type]
            cited_evidence_ids=self._cited_evidence_ids,
            rationale=self._rationale,
            review_priority="normal",
        )

    def adjudicate_claim(self, claim: Claim, evidence: list[EvidenceCandidate], prior_decisions):
        return self.evaluate_claim(claim, evidence)


def _claim(text: str, ambiguous: bool = False) -> Claim:
    return Claim(
        claim_id="claim-1",
        text=text,
        source_span=TextSpan(0, len(text), text),
        response_span=text,
        ambiguous=ambiguous,
        ambiguity_reasons=["compound"] if ambiguous else [],
    )


def _evidence() -> list[EvidenceCandidate]:
    return [
        EvidenceCandidate(
            evidence_id="e-1",
            document_id="case",
            source_path=Path("/tmp/case.txt"),
            snippet="The student receives daily reading intervention.",
            page_number=1,
            section="Services",
            block_kind="paragraph",
            retrieval_rank=1,
            fused_score=0.8,
            lexical_score=1.5,
            semantic_score=0.7,
        )
    ]


def test_multijudge_evaluator_uses_heuristic_when_no_judges() -> None:
    evaluator = MultiJudgeEvaluator(config=EvaluationConfig())
    assessment = evaluator.evaluate(_claim("The student receives daily reading intervention."), _evidence())

    assert assessment.agreement_status == "heuristic"
    assert assessment.label in {"explicit", "inferred"}
    assert assessment.judge_decisions[0].judge_id == "heuristic"


def test_multijudge_evaluator_marks_consensus() -> None:
    judges = [
        FakeJudge("judge-a", "explicit", ["e-1"], "Directly supported."),
        FakeJudge("judge-b", "explicit", ["e-1"], "Directly supported."),
    ]
    evaluator = MultiJudgeEvaluator(config=EvaluationConfig(), judges=judges)
    assessment = evaluator.evaluate(_claim("The student receives daily reading intervention."), _evidence())

    assert assessment.agreement_status == "consensus"
    assert assessment.label == "explicit"
    assert assessment.cited_evidence_ids == ["e-1"]


def test_multijudge_evaluator_contested_resolution_uses_midpoint() -> None:
    judges = [
        FakeJudge("judge-a", "explicit", ["e-1"], "Direct match."),
        FakeJudge("judge-b", "unsupported", [], "No support."),
    ]
    evaluator = MultiJudgeEvaluator(config=EvaluationConfig(), judges=judges)
    assessment = evaluator.evaluate(_claim("The student receives daily reading intervention."), _evidence())

    assert assessment.agreement_status == "contested"
    assert assessment.label == "inferred"
    assert assessment.review_priority == "high"


def test_multijudge_evaluator_uses_adjudicator_when_available() -> None:
    judges = [
        FakeJudge("judge-a", "explicit", ["e-1"], "Direct match."),
        FakeJudge("judge-b", "unsupported", [], "No support."),
    ]
    adjudicator = FakeJudge("judge-c", "explicit", ["e-1"], "Adjudicated as explicit.")
    evaluator = MultiJudgeEvaluator(config=EvaluationConfig(), judges=judges, adjudicator=adjudicator)
    assessment = evaluator.evaluate(_claim("The student receives daily reading intervention."), _evidence())

    assert assessment.agreement_status == "adjudicated"
    assert assessment.label == "explicit"
    assert assessment.judge_decisions[-1].judge_id == "judge-c"


def test_multijudge_evaluator_elevates_ambiguous_claims() -> None:
    judges = [FakeJudge("judge-a", "inferred", ["e-1"], "Relevant support.")]
    evaluator = MultiJudgeEvaluator(config=EvaluationConfig(), judges=judges)
    assessment = evaluator.evaluate(_claim("This should continue when frustration increases.", ambiguous=True), _evidence())

    assert assessment.review_priority == "high"
    assert any(finding.code == "evaluation-ambiguous-claim" for finding in assessment.validation_findings)
