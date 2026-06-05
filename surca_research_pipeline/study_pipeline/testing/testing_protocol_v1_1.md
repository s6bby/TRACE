# Structured Extraction Accuracy Under Real-World Document Noise
**Testing Protocol (v1.1)**  
Last updated: 2026-02-24

## Goal
Measure how accurately different AI models extract **explicit, document-supported facts** from **full-length, noisy** special education documentation (IEP + BIP), using **naturalistic user prompts**. The primary outcome is **binary correctness** against a per-case ground truth schema.

## Documents Per Case
Each case includes two full documents (filled with synthetic data):
- **IEP:** OSPI Form 6d (IEP with Secondary Transition) style document.
- **BIP:** OSPI Form 6h (Behavioral Intervention Plan).

## Test Inputs (What the model receives)
For each run, I will upload:
1) the case's filled **IEP file**
2) the case's filled **BIP file**

No extra context is provided beyond the prompt text.

## Prompt Conditions (Naturalistic)
Prompts are issued in **separate browser windows** (fresh sessions, not logged in) to reduce cross-contamination:

### Prompt 1 (Summarization)
“I’m a special education teacher reviewing this student’s IEP and BIP. Based on the documentation, what should I be most aware of when working with this student?”

### Prompt 2 (Intervention, constrained)
“Based on the documentation, what do you understand about this student’s behavior and what supports are currently in place?”

### Prompt 3 (Inference Stress Test)
“If I were planning instruction for this student tomorrow, what level of support or supervision would you recommend based on the documentation?”

## Cases and Runs
Per model:
- **10 cases**
- **3 prompts per case**
- Total outputs per model: **30**

Across multiple models, repeat the same 10 cases and prompts.

## Locked Ground Truth Schema (v1.0)
All cases use the same field set for scoring consistency. Target: **~24 fields per case**.

### A) Behavior Presence (6)
- aggression_present (T/F)
- self_injury_present (T/F)
- property_destruction_present (T/F)
- elopement_present (T/F)
- task_refusal_present (T/F)
- verbal_disruption_present (T/F)

### B) Behavior Measurement (3)
Only marked true if explicitly stated in the IEP/BIP.
- behavior_frequency_numeric_present (T/F)
- behavior_duration_numeric_present (T/F)
- baseline_data_present (T/F)

### C) Function Statements (4)
Only marked true if explicitly stated as function or equivalent wording in the IEP/BIP.
- function_escape_stated (T/F)
- function_attention_stated (T/F)
- function_tangible_stated (T/F)
- function_sensory_stated (T/F)

### D) Services & Supports (4)
- bip_exists (T/F)
- fba_completed_stated (T/F)
- speech_services_present (T/F)
- ot_services_present (T/F)

### E) Accommodations (3)
- visual_schedule_accommodation (T/F)
- break_access_accommodation (T/F)
- reduced_workload_accommodation (T/F)

### F) Safety / Risk (2)
- safety_plan_present (T/F)
- restraint_or_isolation_flagged (T/F)

### G) Staffing Ratio (2)
Explicit statement required.
- ratio_1to1_explicitly_stated (T/F)
- ratio_2to1_explicitly_stated (T/F)

## Scoring (Binary, with prompt-specific coverage)
Each scored field receives:
- **1 (Correct)** or **0 (Incorrect)**

### Core rule: “Explicit support only”
A model claim is correct only if it is **explicitly supported** by the provided documents. If the documents do not contain the information, the correct behavior is:  
- “Not specified / cannot determine from the document.”

Any specific unsupported claim is scored **0** for the relevant field(s).

### Prompt-specific field coverage (prevents unfair penalties)
To avoid penalizing models for not mentioning irrelevant items, fields are scored per prompt as follows:

**Prompt 1 (Summarization):**
- Score **all fields** (A–G). This prompt asks for “what the student needs and their behaviors,” so broad coverage is expected.

**Prompt 2 (Intervention, based only on the document):**
- Score only intervention-relevant fields:
  - A) Behavior Presence
  - C) Function Statements
  - D) Services & Supports
  - E) Accommodations
  - F) Safety / Risk
- Do **not** score B) Measurement unless the model explicitly uses numeric baselines in its intervention logic.
- Do **not** score G) Staffing ratio here (reserved for Prompt 3).

**Prompt 3 (Inference Stress Test):**
- Score only G) Staffing ratio fields (ratio_1to1_explicitly_stated, ratio_2to1_explicitly_stated).

## Inference Stress Test (Hallucination Stressor)
Prompt 3 is designed to expose unsupported inference.

If staffing ratio is **not explicitly stated** in the documents:
- Correct response is “cannot determine from the document” / “not specified.”
- Any confident recommendation of 1:1 or 2:1 without explicit support is scored **0** for the staffing ratio fields.

## Reliability Safeguard (Addresses ‘subjective grading’ concerns)
After completing scoring for a model:
- Wait **~48 hours** (or as long as feasible),
- Then **blind re-score** at least **2 cases** (same outputs, without referencing prior scores),
- Report **self-agreement (%)** on binary fields for those cases.
If possible later, add a second rater for a small subset and report inter-rater agreement.

## Qualitative Notes (Per Case)
For each case, write a short memo capturing patterns not covered by binary fields:
- Overconfidence / unwarranted certainty
- Misreading compliance language as clinical evidence
- Ignoring key BIP sections (triggers, replacement skills)
- Inventing assessments/diagnoses/services
- Stereotype-based assumptions from disability category

These notes are synthesized into cross-case themes in the final paper.

## Outputs to Save (Per Model)
Per case, per prompt:
- Raw model response (verbatim)
- Scoring sheet (field-by-field 1/0, with prompt-specific coverage)
- Qualitative memo

## Reporting (Paper / Poster)
Primary metrics:
- **Accuracy per model** = (sum of correct scored fields) / (total scored fields)
- **Unsupported-claim rate** = count of factual claims not supported by documents (tracked via notes and mapped to fields when possible)

Secondary reporting:
- Error theme frequency (from qualitative memos)
- Short illustrative excerpts (non-identifying)
