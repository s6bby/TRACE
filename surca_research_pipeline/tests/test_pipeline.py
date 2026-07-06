import csv
import json
from pathlib import Path

import pytest
from docx import Document

from surca_research_pipeline.src.pipeline.scoring_rules import FIELD_ORDER
from surca_research_pipeline.src.pipeline.special_ed_pipeline_hardened import (
    extract_fields_with_evidence,
    get_scored_fields,
    load_prompts,
    run_extract_only,
    run_preflight_validation,
    safe_model_name,
    write_run_report,
)

ROOT = Path(__file__).resolve().parents[2]
REAL_BASE_DIR = ROOT / "surca_research_pipeline" / "study_pipeline"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def make_ground_truth(**overrides):
    payload = {field: False for field in FIELD_ORDER}
    payload.update(overrides)
    payload["case_id"] = "CASE001"
    return payload


def write_docx(path: Path, lines):
    doc = Document()
    for line in lines:
        doc.add_paragraph(line)
    doc.save(path)


def build_minimal_dataset(base_dir: Path):
    case_dir = base_dir / "cases" / "CASE001"
    prompt_dir = base_dir / "master_prompts"
    case_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir.mkdir(parents=True, exist_ok=True)

    write_docx(case_dir / "CASE001_IEP.docx", ["Student uses a visual schedule."])
    write_docx(case_dir / "CASE001_BIP.docx", ["A BIP is in place and behavior occurs 2 times per day."])
    (case_dir / "case001.json").write_text(
        json.dumps(make_ground_truth(bip_exists=True, visual_schedule_accommodation=True), indent=2),
        encoding="utf-8",
    )

    (prompt_dir / "PROMPT 1.md").write_text("Prompt 1", encoding="utf-8")
    (prompt_dir / "PROMPT 2.md").write_text("Prompt 2", encoding="utf-8")
    (prompt_dir / "PROMPT 3.md").write_text("Prompt 3", encoding="utf-8")


def test_load_prompts_reads_clean_text():
    prompts = load_prompts(REAL_BASE_DIR)

    assert prompts["prompt_1"].startswith("I'm a special education teacher")
    assert all("â" not in text for text in prompts.values())


def test_extract_fields_from_broad_fixture():
    predicted, evidence, abstention_hits = extract_fields_with_evidence(read_fixture("response_broad_summary.txt"))

    assert predicted["aggression_present"] is True
    assert predicted["verbal_disruption_present"] is True
    assert predicted["task_refusal_present"] is True
    assert predicted["behavior_frequency_numeric_present"] is True
    assert predicted["behavior_duration_numeric_present"] is True
    assert predicted["baseline_data_present"] is True
    assert predicted["function_escape_stated"] is True
    assert predicted["function_attention_stated"] is True
    assert predicted["bip_exists"] is True
    assert predicted["ot_services_present"] is True
    assert predicted["visual_schedule_accommodation"] is True
    assert predicted["break_access_accommodation"] is True
    assert predicted["self_injury_present"] is False
    assert predicted["elopement_present"] is False
    assert evidence["aggression_present"]["positive_hits"]
    assert evidence["self_injury_present"]["negative_hits"]
    assert abstention_hits == []


def test_extract_fields_records_abstention_language():
    predicted, _, abstention_hits = extract_fields_with_evidence(read_fixture("response_ratio_abstain.txt"))

    assert predicted["ratio_1to1_explicitly_stated"] is False
    assert predicted["ratio_2to1_explicitly_stated"] is False
    assert {item["label"] for item in abstention_hits} >= {"cannot_determine", "not_specified"}


def test_prompt_specific_scoring_coverage():
    assert len(get_scored_fields("prompt_1")) == 24
    assert len(get_scored_fields("prompt_2")) == 19
    assert get_scored_fields("prompt_3") == [
        "ratio_1to1_explicitly_stated",
        "ratio_2to1_explicitly_stated",
    ]


def test_safe_model_name_removes_windows_problem_characters():
    assert safe_model_name("us.amazon.nova-micro-v1:0") == "us.amazon.nova-micro-v1_0"
    assert safe_model_name("mistralai/mistral-nemo-instruct-2407") == "mistralai_mistral-nemo-instruct-2407"


def test_preflight_validation_rejects_missing_case():
    with pytest.raises(ValueError, match="Selected case folders were not found"):
        run_preflight_validation(REAL_BASE_DIR, ["CASE999"], validate_prompts=True)


def test_run_extract_only_creates_run_folder(tmp_path: Path):
    base_dir = tmp_path / "study_pipeline"
    build_minimal_dataset(base_dir)

    run_extract_only(base_dir, None, "extract_test_run", False)

    run_dir = base_dir / "outputs" / "runs" / "extract_test_run"
    manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))

    assert run_dir.exists()
    assert (run_dir / "extracted_case_text" / "CASE001__IEP_extracted.txt").exists()
    assert (run_dir / "field_rules.json").exists()
    assert manifest["status"] == "completed"
    assert manifest["completed_case_count"] == 1


def test_write_run_report_creates_reproducible_files(tmp_path: Path):
    run_dir = tmp_path / "sample_run"
    run_dir.mkdir()

    with open(run_dir / "results.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "timestamp",
                "case_id",
                "model_name",
                "prompt_id",
                "prompt_label",
                "scored_field_count",
                "correct_scored_fields",
                "accuracy_percent",
                "abstention_detected",
                "abstention_hits",
                "raw_response_sha256",
                "predicted_json_sha256",
            ]
        )
        writer.writerow(
            [
                "2026-01-01T00:00:00",
                "CASE001",
                "demo-model",
                "prompt_1",
                "Broad teacher summary",
                "24",
                "18",
                "75.0",
                "False",
                "",
                "raw1",
                "pred1",
            ]
        )
        writer.writerow(
            [
                "2026-01-01T00:00:01",
                "CASE002",
                "demo-model",
                "prompt_3",
                "Support level recommendation",
                "2",
                "2",
                "100.0",
                "True",
                "cannot_determine:cannot determine",
                "raw2",
                "pred2",
            ]
        )

    with open(run_dir / "field_results.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "timestamp",
                "case_id",
                "model_name",
                "prompt_id",
                "prompt_label",
                "field_name",
                "field_label",
                "scored_in_prompt",
                "predicted",
                "ground_truth",
                "is_match",
                "positive_hits",
                "negative_hits",
                "matched_positive_patterns",
                "matched_negative_patterns",
            ]
        )
        writer.writerow(
            [
                "2026-01-01T00:00:00",
                "CASE001",
                "demo-model",
                "prompt_1",
                "Broad teacher summary",
                "aggression_present",
                "Aggression present",
                "True",
                "True",
                "False",
                "False",
                "aggression",
                "",
                "\\baggression\\b",
                "",
            ]
        )

    metrics = write_run_report(run_dir)

    assert (run_dir / "result_summary.md").exists()
    assert (run_dir / "summary_metrics.json").exists()
    assert metrics["total_evaluations"] == 2
    assert metrics["overall_average_accuracy"] == 87.5
