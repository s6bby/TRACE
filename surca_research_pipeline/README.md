# TRACE-ED Run Guide

This folder contains the TRACE-ED pipeline code.

The original DOCX/PDF form templates are not included in the public repo. The case documents are synthetic, but the form templates are licensed, so the repository keeps only safe code, answer keys, demo data, and extracted plain-text examples.

Edit these first in:

```text
surca_research_pipeline\src\runtime\run_config.json
```

Change:
- `base_url`
- `model`
- `run_cases`
- `run_id`

First-time setup:

```bat
/repoRoot
surca_research_pipeline\src\runtime\run_surca.bat setup
```

LM Studio:
1. Open LM Studio.
2. Load the model you want to test.
3. Start the local server.
4. Copy the model ID into `src\runtime\run_config.json`.
5. Use the server URL shown by LM Studio.

Workflow:

1. Edit `src\runtime\run_config.json`
2. Start LM Studio and load the model
3. Run `verify`
4. Run `run`
5. Open `demo` if you want to present the results

Code layout:

- `src\runtime\`
  run config and runner files
- `src\pipeline\`
  main pipeline code
- `src\claims\`
  claim extraction work

Verify everything is ready:

```bat
surca_research_pipeline\src\runtime\run_surca.bat verify
```

Run the configured test batch:

```bat
surca_research_pipeline\src\runtime\run_surca.bat run
```

Run again with the same run id:

```bat
surca_research_pipeline\src\runtime\run_surca.bat run --overwrite
```

Optional custom run id:

```bat
surca_research_pipeline\src\runtime\run_surca.bat run --run-id my_model_run
```

Start the demo:

```bat
surca_research_pipeline\src\runtime\run_surca.bat demo
```
