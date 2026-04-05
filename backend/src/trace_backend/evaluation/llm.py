"""Local LLM client support for TRACE evaluation."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
import os
import re
from urllib import request

from trace_backend.claims.models import Claim
from trace_backend.evaluation.models import JudgeConfig
from trace_backend.evaluation.prompts import build_adjudication_messages, build_claim_evaluation_messages
from trace_backend.pipeline.models import EvidenceCandidate, JudgeDecision

JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json_object(raw_text: str) -> dict[str, object]:
    match = JSON_OBJECT_RE.search(raw_text)
    if match is None:
        raise ValueError("Judge response did not contain a JSON object.")
    return json.loads(match.group(0))


@dataclass(slots=True)
class OpenAICompatibleJudge:
    """A local OpenAI-compatible chat-completions client."""

    config: JudgeConfig

    def _request(self, messages: list[dict[str, str]]) -> str:
        endpoint = self.config.base_url.rstrip("/") + "/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        payload = json.dumps(
            {
                "model": self.config.model,
                "messages": messages,
                "temperature": 0,
            }
        ).encode("utf-8")
        http_request = request.Request(endpoint, data=payload, headers=headers, method="POST")

        with request.urlopen(http_request, timeout=self.config.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))

        choices = body.get("choices", [])
        if not choices:
            raise ValueError("Judge endpoint returned no choices.")

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, list):
            content = "\n".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            )
        return str(content)

    def evaluate_claim(self, claim: Claim, evidence: list[EvidenceCandidate]) -> JudgeDecision:
        raw_text = self._request(build_claim_evaluation_messages(claim, evidence))
        parsed = _extract_json_object(raw_text)
        return JudgeDecision(
            judge_id=self.config.judge_id,
            label=str(parsed.get("label", "unsupported")),  # type: ignore[arg-type]
            cited_evidence_ids=[str(item) for item in parsed.get("cited_evidence_ids", [])],
            rationale=str(parsed.get("rationale", "")),
            ambiguity_note=str(parsed.get("ambiguity_note", "")),
            review_priority=str(parsed.get("review_priority", "normal")),  # type: ignore[arg-type]
            metadata={"raw_response": raw_text},
        )

    def adjudicate_claim(
        self,
        claim: Claim,
        evidence: list[EvidenceCandidate],
        prior_decisions: list[JudgeDecision],
    ) -> JudgeDecision:
        raw_text = self._request(build_adjudication_messages(claim, evidence, prior_decisions))
        parsed = _extract_json_object(raw_text)
        return JudgeDecision(
            judge_id=self.config.judge_id,
            label=str(parsed.get("label", "unsupported")),  # type: ignore[arg-type]
            cited_evidence_ids=[str(item) for item in parsed.get("cited_evidence_ids", [])],
            rationale=str(parsed.get("rationale", "")),
            ambiguity_note=str(parsed.get("ambiguity_note", "")),
            review_priority=str(parsed.get("review_priority", "high")),  # type: ignore[arg-type]
            metadata={"raw_response": raw_text, "adjudicator": True},
        )

    @classmethod
    def from_env(cls, prefix: str) -> "OpenAICompatibleJudge | None":
        base_url = os.getenv(f"{prefix}_BASE_URL")
        model = os.getenv(f"{prefix}_MODEL")
        if not base_url or not model:
            return None

        return cls(
            JudgeConfig(
                judge_id=prefix.lower(),
                base_url=base_url,
                model=model,
                api_key=os.getenv(f"{prefix}_API_KEY"),
                timeout_seconds=float(os.getenv(f"{prefix}_TIMEOUT", "60")),
            )
        )


def load_local_judges_from_env() -> tuple[list[OpenAICompatibleJudge], OpenAICompatibleJudge | None]:
    """Load up to two local judges plus an optional adjudicator from environment variables."""

    judges = [
        judge
        for judge in [
            OpenAICompatibleJudge.from_env("TRACE_JUDGE_1"),
            OpenAICompatibleJudge.from_env("TRACE_JUDGE_2"),
        ]
        if judge is not None
    ]
    adjudicator = OpenAICompatibleJudge.from_env("TRACE_ADJUDICATOR")
    return judges, adjudicator


def run_judges_parallel(
    judges: list[OpenAICompatibleJudge],
    claim: Claim,
    evidence: list[EvidenceCandidate],
) -> list[JudgeDecision]:
    """Run local judges in parallel for one claim."""

    if not judges:
        return []

    with ThreadPoolExecutor(max_workers=len(judges)) as executor:
        futures = [executor.submit(judge.evaluate_claim, claim, evidence) for judge in judges]
        return [future.result() for future in futures]
