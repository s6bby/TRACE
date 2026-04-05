"""Pydantic schemas for the TRACE API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ClaimsRequest(BaseModel):
    """Request body for claim extraction."""

    response_text: str = Field(..., min_length=1)


class AnalyzeByPathRequest(BaseModel):
    """Request body for file-path based backend analysis."""

    case_id: str = "analysis"
    response_text: str = Field(..., min_length=1)
    document_paths: list[str] = Field(..., min_length=1)
