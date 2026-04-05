# TRACE

TRACE is an early-stage research repository for a claim-level reliability framework for document-grounded large language model outputs. The project studies whether LLM responses can be made more traceable and interpretable by decomposing them into claims, linking those claims to source evidence, and labeling them as `explicit`, `inferred`, or `unsupported`.

The initial evaluation domain is special education document interpretation, especially IEPs and BIPs, used as a high-stakes test-bed for the broader framework.

## Repository Layout

```text
.
├── data/
├── docs/
│   ├── abstracts/
│   ├── applications/
│   ├── archive/
│   ├── methods/
│   └── planning/
├── results/
├── src/
│   └── trace_core/
│       └── pipeline/
└── tests/
```

## Current Scope

This repository is intentionally lightweight. The current version is designed to support:

- research framing and documentation
- modular backend development
- future evaluation experiments
- a clean path to a public GitHub repository

## Code Structure

The initial package skeleton separates the core responsibilities of the framework:

- `trace_core/schemas.py`: shared data models
- `trace_core/pipeline/claims.py`: claim extraction stage
- `trace_core/pipeline/retrieval.py`: evidence retrieval stage
- `trace_core/pipeline/evaluation.py`: claim assessment stage
- `trace_core/pipeline/reporting.py`: report generation stage
- `trace_core/orchestrator.py`: pipeline coordination

## Documentation

The current research packet lives under [`docs/`](docs/README.md).

Primary documents:

- [`docs/abstracts/trace-v1-project-abstract.md`](docs/abstracts/trace-v1-project-abstract.md)
- [`docs/abstracts/trace-one-page-summary.md`](docs/abstracts/trace-one-page-summary.md)
- [`docs/methods/trace-methods-and-evaluation-plan.md`](docs/methods/trace-methods-and-evaluation-plan.md)
- [`docs/planning/trace-next-steps-and-supporting-docs.md`](docs/planning/trace-next-steps-and-supporting-docs.md)

## Getting Started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Data Handling Note

The repository is structured for synthetic, sanitized, or de-identified materials. Sensitive student records should not be committed to version control.
