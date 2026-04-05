from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from trace_backend.api.app import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_claims_endpoint_returns_claims() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/claims",
        json={"response_text": "Student Summary\n\nThe student receives reading support."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["metrics"]["claim_count"] == 1
    assert payload["claims"][0]["text"] == "The student receives reading support."


def test_analyze_by_path_endpoint_runs_pipeline(tmp_path: Path) -> None:
    document_path = tmp_path / "case.txt"
    document_path.write_text(
        "Services\n\nThe student receives daily reading intervention.\n\nTransportation is provided by bus.",
        encoding="utf-8",
    )

    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analyze/by-path",
        json={
            "case_id": "api-case",
            "response_text": "The student receives daily reading intervention.\nExtended time is available.",
            "document_paths": [str(document_path)],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["case_id"] == "api-case"
    assert payload["summary"]["total_claims"] == 2
    assert len(payload["assessments"]) == 2


def test_analyze_endpoint_accepts_uploads(tmp_path: Path) -> None:
    document_path = tmp_path / "case.txt"
    document_path.write_text("Services\n\nThe student receives daily reading intervention.", encoding="utf-8")

    client = TestClient(create_app())
    with document_path.open("rb") as handle:
        response = client.post(
            "/api/v1/analyze",
            data={
                "case_id": "upload-case",
                "response_text": "The student receives daily reading intervention.",
            },
            files={"documents": ("case.txt", handle, "text/plain")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["case_id"] == "upload-case"
    assert payload["summary"]["explicit_count"] >= 1
