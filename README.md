# TRACE

TRACE is a claim-level reliability framework for document-grounded AI outputs.
It scans uploaded source documents, extracts claims from a response, retrieves
candidate evidence, and produces a structured report showing which claims appear
explicitly supported, inferred, or unsupported.

This repository contains both:

- a Vite + React frontend for the demo interface
- a FastAPI + Python backend for document scanning, claim extraction,
  retrieval, evaluation, and deterministic validation

The current demo supports `PDF`, `DOCX`, and `TXT` uploads through the web app.

## What TRACE Does

- scans and normalizes source documents for downstream review
- decomposes a response into claim-sized units
- retrieves supporting evidence from the uploaded corpus
- builds a claim-by-claim report instead of collapsing everything into one score
- surfaces ambiguity, retrieval warnings, and validation findings for human review

## Current Architecture

```text
.
├── backend/
│   ├── src/trace_backend/
│   │   ├── api/
│   │   ├── benchmark/
│   │   ├── claims/
│   │   ├── evaluation/
│   │   ├── pipeline/
│   │   ├── retrieval/
│   │   └── scanning/
│   ├── data/synthetic-eval/
│   └── tests/
├── src/
│   ├── components/
│   ├── content/
│   ├── lib/
│   ├── App.tsx
│   ├── main.tsx
│   └── styles.css
├── documentation/
│   └── trace-research/
├── package.json
└── vite.config.ts
```

## Running Locally

From the repository root:

```bash
python3 -m venv .venv
./.venv/bin/pip install -e backend
npm install
npm run dev
```

That starts:

- the FastAPI backend on `http://127.0.0.1:8000`
- the Vite frontend on `http://localhost:5173`

Open `http://localhost:5173` and run TRACE through the web app.

## Backend Commands

Run the benchmark:

```bash
./.venv/bin/trace-benchmark --pretty
```

Run the API only:

```bash
./.venv/bin/trace-api --host 127.0.0.1 --port 8000 --reload
```

Run a CLI analysis:

```bash
./.venv/bin/trace-analyze \
  --case-id demo \
  --document path/to/document.pdf \
  --response-path path/to/response.txt \
  --pretty
```

## Frontend Editing Surface

- `src/App.tsx`: app flow and page composition
- `src/styles.css`: theme, layout, and visual system
- `src/components/`: reusable UI blocks
- `src/content/siteContent.ts`: user-facing copy
- `src/lib/api.ts`: frontend/backend API integration
- `src/lib/trace.ts`: report summarization and terminal log mapping
- `src/lib/types.ts`: frontend report types

## Backend Entry Points

- `backend/src/trace_backend/scanning/`: document scanning and OCR safeguards
- `backend/src/trace_backend/claims/`: claim extraction and claim validation
- `backend/src/trace_backend/retrieval/`: lexical and hybrid evidence retrieval
- `backend/src/trace_backend/evaluation/`: current evaluator layer
- `backend/src/trace_backend/pipeline/`: final report assembly and validation
- `backend/src/trace_backend/api/`: FastAPI service
- `backend/src/trace_backend/benchmark/`: synthetic benchmark harness

## Verification

The current repo has been verified with:

```bash
./.venv/bin/python -m pytest backend/tests -q
npm run build
```

## Research Context

The initial evaluation domain is high-stakes special education document
interpretation, especially IEPs and BIPs. The broader goal is a framework for
evidence-grounded review of AI outputs where unsupported claims need to be made
visible rather than hidden behind a single aggregate judgment.

The older research scaffold and Streamlit prototype remain under
`documentation/trace-research/` for reference.

## License and Use Restrictions

This repository is not open source. The code is shared for educational review
only under the custom terms in [LICENSE](LICENSE).

You may inspect the code and run it locally for personal, non-commercial
evaluation. You may not use, deploy, redistribute, modify for public use, or
commercialize this project without prior written permission from the copyright
holder.

If you need stricter access control than GitHub's normal public-repository
visibility and forking behavior, keep the repository private.
