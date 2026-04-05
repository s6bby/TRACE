"""FastAPI application for TRACE backend services."""

from __future__ import annotations

from contextlib import asynccontextmanager
import os
from pathlib import Path
import shutil
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from trace_backend.api.schemas import AnalyzeByPathRequest, ClaimsRequest
from trace_backend.api.serialization import serialize
from trace_backend.claims import extract_claims
from trace_backend.pipeline.orchestrator import TraceAnalysisPipeline
from trace_backend.scanning import DocumentScanner


def _cors_origins() -> list[str]:
    raw = os.getenv(
        "TRACE_API_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://ovystudio.com,https://www.ovystudio.com",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _persist_uploads(files: list[UploadFile]) -> tuple[tempfile.TemporaryDirectory[str], list[Path]]:
    tempdir = tempfile.TemporaryDirectory(prefix="trace-api-")
    stored_paths: list[Path] = []
    for index, upload in enumerate(files, start=1):
        suffix = Path(upload.filename or f"document-{index}").suffix or ".txt"
        safe_name = Path(upload.filename or f"document-{index}{suffix}").name
        path = Path(tempdir.name) / safe_name
        with path.open("wb") as handle:
            shutil.copyfileobj(upload.file, handle)
        stored_paths.append(path)
    return tempdir, stored_paths


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.document_scanner = DocumentScanner()
    app.state.analysis_pipeline = TraceAnalysisPipeline()
    yield


def create_app() -> FastAPI:
    """Create the TRACE FastAPI application."""

    app = FastAPI(title="TRACE Backend API", version="0.1.0", lifespan=lifespan)
    app.state.document_scanner = DocumentScanner()
    app.state.analysis_pipeline = TraceAnalysisPipeline()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/v1/claims")
    async def claims_endpoint(request: ClaimsRequest):
        return serialize(extract_claims(request.response_text))

    @app.post("/api/v1/scan")
    async def scan_endpoint(documents: list[UploadFile] = File(...)):
        scanner: DocumentScanner = app.state.document_scanner
        tempdir, stored_paths = _persist_uploads(documents)
        try:
            results = [scanner.scan_path(path) for path in stored_paths]
            return serialize(results)
        finally:
            tempdir.cleanup()

    @app.post("/api/v1/analyze")
    async def analyze_endpoint(
        response_text: str = Form(...),
        documents: list[UploadFile] = File(...),
        case_id: str = Form("analysis"),
    ):
        scanner: DocumentScanner = app.state.document_scanner
        pipeline: TraceAnalysisPipeline = app.state.analysis_pipeline
        tempdir, stored_paths = _persist_uploads(documents)
        try:
            scanned_documents = [scanner.scan_path(path) for path in stored_paths]
            report = pipeline.analyze_response(case_id, response_text, scanned_documents)
            return serialize(report)
        finally:
            tempdir.cleanup()

    @app.post("/api/v1/analyze/by-path")
    async def analyze_by_path_endpoint(request: AnalyzeByPathRequest):
        scanner: DocumentScanner = app.state.document_scanner
        pipeline: TraceAnalysisPipeline = app.state.analysis_pipeline

        if not request.document_paths:
            raise HTTPException(status_code=400, detail="At least one document path is required.")

        try:
            scanned_documents = [scanner.scan_path(path) for path in request.document_paths]
        except (FileNotFoundError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        report = pipeline.analyze_response(request.case_id, request.response_text, scanned_documents)
        return serialize(report)

    return app


app = create_app()
