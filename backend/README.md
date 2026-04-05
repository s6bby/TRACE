# TRACE Backend

This package contains the backend ingestion and scanning layer for TRACE.

The current backend focus is document preparation, because the project
documentation makes preprocessing quality part of the method rather than an
implementation detail. If the scanner distorts the source material, later claim
retrieval and support labels become unreliable for the wrong reasons.

The next backend focus is claim decomposition, because the TRACE roadmap treats
claim-boundary stability as a methodological concern rather than a solved text
processing detail. The backend now includes a dedicated claim extractor that
preserves source spans, flags ambiguous decomposition, and validates claim
structure before retrieval.

## Current Scanner Goals

- support `PDF`, `DOCX`, and `TXT`
- preserve useful structure such as headings, paragraphs, tables, and page
  locations when available
- compare multiple extraction paths for PDFs to expose disagreement rather than
  silently trust one parser
- surface pages that likely require OCR or multimodal follow-up because they are
  image-heavy or text-light
- return a structured scan result that downstream TRACE stages can consume

## Current Redundancy Safeguards

- `PyMuPDF` is used as the primary PDF text extractor
- `pdfplumber` is used as a verification extractor and table detector
- `RapidOCR` is used as an OCR backstop on image-heavy PDF pages where native
  text extraction appears incomplete
- `RapidOCR` is also used on embedded DOCX images so scanned exhibits and
  graphic-heavy Word files do not silently drop text
- the scanner computes per-page similarity between extractors and emits findings
  when disagreement is too high
- pages with image-heavy layouts and weak extracted text are OCR'd and still
  flagged for multimodal or manual review when ambiguity remains

## Future Multimodal Layer

The current implementation does not call external AI models yet. Instead, it
lays the groundwork for them by:

- preserving page-level structure and metadata
- recording extraction disagreements and ambiguity findings
- returning a normalized representation that a later multimodal verifier can
  inspect against the original document

That keeps v1 aligned with the research plan: build a minimum reliable pipeline
first, then add constrained model-based validation on top of a trustworthy
ingestion layer.

## Claim Extraction Stage

The claim extractor currently takes a raw model response and returns:

- discrete claims with exact character spans back to the original response
- claim types such as `statement`, `list_item`, `recommendation`, and
  `obligation`
- ambiguity markers for conditional, referential, compound, or enumeration-like
  claims
- suggested subclaims when TRACE can propose a safer decomposition without
  pretending the boundary is certain
- deterministic validation findings for duplicate ids, broken spans, and empty
  claims

Use the CLI with:

```bash
trace-claims --path response.txt --pretty
```

## Retrieval and Evaluation Stage

The backend now also includes:

- hybrid evidence retrieval over scanned blocks and tables
- lexical scoring by default so retrieval remains deterministic and debuggable
- optional local embedding support for semantic retrieval through an
  OpenAI-compatible `/embeddings` endpoint
- a multi-judge evaluator that can call two local judge models plus an optional
  adjudicator through OpenAI-compatible `/chat/completions` endpoints
- deterministic citation validation so model outputs are checked against the
  retrieved evidence ids before the report is trusted

Run the current end-to-end backend pipeline with:

```bash
trace-analyze --case-id demo --document case.pdf --response-path response.txt --pretty
```

## Deterministic Validation and Reporting

The pipeline now finishes with a deterministic report-building layer that:

- re-validates final citations against the scanned source text
- flags missing citations, missing source documents, weak evidence scores, and
  unresolved disagreement states
- computes report-level metrics such as evidence coverage, citation validity,
  ambiguity count, and high-priority review count
- keeps retrieval warnings separate from final support labels so retrieval
  failure can be analyzed on its own

## FastAPI Service

The backend now includes a FastAPI service for the frontend and local testing.

Run it with:

```bash
trace-api --host 127.0.0.1 --port 8000 --reload
```

Available endpoints:

- `GET /health`
- `POST /api/v1/claims`
- `POST /api/v1/scan`
- `POST /api/v1/analyze`
- `POST /api/v1/analyze/by-path`

The default CORS allowlist includes local Vite development plus:

- `https://ovystudio.com`
- `https://www.ovystudio.com`

Override it with:

```bash
TRACE_API_CORS_ORIGINS=http://localhost:5173,https://ovystudio.com
```

## Synthetic Benchmark

The backend includes a small synthetic evaluation dataset so you can smoke-test
the full pipeline before wiring in local models.

Default dataset path:

```text
backend/data/synthetic-eval
```

Run the benchmark with:

```bash
trace-benchmark --pretty
```

Optional CSV output:

```bash
trace-benchmark --csv benchmark-results.csv --pretty
```

The benchmark currently reports:

- claim precision and recall
- label accuracy
- retrieval recall at `k`
- citation validity rate

### Local Model Setup

You do not need local models to run the pipeline. Without them, TRACE uses:

- lexical retrieval only
- a deterministic heuristic evaluator

When you are ready to enable local-model support, provide:

- one local embedding model exposed through an OpenAI-compatible
  `/embeddings` endpoint
- one or two local judge models exposed through OpenAI-compatible
  `/chat/completions` endpoints
- optionally, a third local adjudicator model for disagreements

Environment variables:

```bash
TRACE_EMBED_BASE_URL=
TRACE_EMBED_MODEL=
TRACE_EMBED_API_KEY=

TRACE_JUDGE_1_BASE_URL=
TRACE_JUDGE_1_MODEL=
TRACE_JUDGE_1_API_KEY=

TRACE_JUDGE_2_BASE_URL=
TRACE_JUDGE_2_MODEL=
TRACE_JUDGE_2_API_KEY=

TRACE_ADJUDICATOR_BASE_URL=
TRACE_ADJUDICATOR_MODEL=
TRACE_ADJUDICATOR_API_KEY=
```
