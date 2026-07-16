# TRACE-ED Run Guide

This folder contains the TRACE-ED pipeline code.

The original DOCX/PDF form templates are not included in the public repo. The case documents are synthetic, but the form templates are licensed, so the repository keeps only safe code, answer keys, demo data, and extracted plain-text examples.

Edit these first in:

```text
surca_research_pipeline\src\runtime\run_config.json
```

Change:
- `provider`
- `model`
- `run_cases`
- `run_id`
- `demo_min_evaluations`

Use run ids that say where the result came from:

```text
aws_nova_micro_cases001_003
aws_nova_lite_cases001_003
local_gemma_cases001_003
```

First-time setup:

```bat
/repoRoot
surca_research_pipeline\src\runtime\run_surca.bat setup
```

Bedrock:
1. In AWS, stay in `us-east-2`.
2. In the AWS access portal, click `Access keys` for `AWSPowerUserAccess`.
3. Copy the temporary credential commands into the same Command Prompt window.
4. In `src\runtime\run_config.json`, use:

```json
"provider": "bedrock",
"aws_region": "us-east-2",
"model": "us.amazon.nova-micro-v1:0"
```

LM Studio:
1. Open LM Studio.
2. Load the model you want to test.
3. Start the local server.
4. In `src\runtime\run_config.json`, use:

```json
"provider": "lmstudio",
"base_url": "http://127.0.0.1:1234",
"model": "YOUR_LM_STUDIO_MODEL_ID"
```

Workflow:

1. Edit `src\runtime\run_config.json`
2. Set AWS credentials for Bedrock, or start LM Studio for local runs
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

After a run finishes, the demo export only includes the provider you just used.
For example, a Bedrock run exports Bedrock runs only, not old LM Studio runs.
Set `demo_min_evaluations` to `30` when you only want full 10-case runs in the demo.

Output folders:

```text
LM Studio runs: surca_research_pipeline\study_pipeline\outputs\runs
Bedrock runs:   surca_research_pipeline\study_pipeline\outputs\bedrock_runs
```

Inside a run folder, check:

```text
cleaned_case_text      text sent to the model
extracted_case_text    raw extracted text
extraction_audits      what cleanup removed
ground_truth_audits    field-by-field audit helper
claims                 claim extraction and support check
review_checklist.md    what to inspect before trusting the run
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
