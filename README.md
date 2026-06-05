# TRACE-ED

TRACE-ED is a research prototype for testing how well language models handle special education-style documents.

The pipeline does four main things:

- extracts text from synthetic IEP/BIP-style case documents
- sends the extracted text to a local LM Studio model
- scores the model response against a small answer key
- splits model responses into checkable claims for review

This repository is focused only on the TRACE-ED prototype code and safe synthetic artifacts.

## Data note

The original DOCX/PDF form templates are not included in this repository. They are licensed template materials and are kept out of GitHub on purpose.

The repository may include synthetic case metadata, synthetic model responses, and plain-text extracted examples. These are for demonstration and testing only and do not represent real students.

## Main folders

- `surca_research_pipeline/src/` contains the Python pipeline, scoring rules, runtime config loader, and claim extraction code.
- `surca_research_pipeline/study_pipeline/master_prompts/` contains the prompts used by the study.
- `surca_research_pipeline/study_pipeline/cases/` contains synthetic answer keys only. The DOCX case forms are ignored.
- `surca_research_pipeline/study_pipeline/plain_text_cases/` contains public-safe extracted text examples.
- `surca_research_pipeline/demo/` contains the simple Vite frontend for inspecting results.
- `surca_research_pipeline/tests/` contains tests for scoring and claim extraction.

## Quick start

Install the Python environment:

```bat
surca_research_pipeline\src\runtime\run_surca.bat setup
```

Edit the run config:

```text
surca_research_pipeline\src\runtime\run_config.json
```

Set:

- `base_url`
- `model`
- `run_cases`
- `run_id`

Verify LM Studio is ready:

```bat
surca_research_pipeline\src\runtime\run_surca.bat verify
```

Run the configured batch:

```bat
surca_research_pipeline\src\runtime\run_surca.bat run
```

Start the demo:

```bat
surca_research_pipeline\src\runtime\run_surca.bat demo
```

More details are in `surca_research_pipeline/README.md`.
