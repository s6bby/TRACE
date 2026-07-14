# TRACE-ED Pipeline Hardening To-Do

This is the list to work through before collecting big results.

The main goal is simple: if someone asks how the score was produced, we should be able to point to the document text, prompt, model response, extracted field, evidence hit, ground truth, and final score.

## 1. Lock The Testing Method

- [x] Write one current testing protocol that matches the automated pipeline.
- [x] Remove or update the older manual-upload language in the testing protocol.
- [x] Define what counts as correct, incorrect, unsupported, abstained, omitted, and unclear.
- [ ] Lock the final prompts before full runs.
- [ ] Lock the 10-case test set before full runs.
- [ ] Lock the first model list before full runs.
- [ ] Lock temperature, max tokens, AWS region, provider, and model IDs.

## 2. Clean And Audit Text Extraction

- [x] Save both raw extracted text and cleaned model-input text.
- [x] Decide what template boilerplate should be removed before model input.
- [x] Specifically review repeated `POINTS TO CONSIDER` sections.
- [x] Specifically review repeated restraint/isolation boilerplate.
- [x] Add extraction stats per case.
- [x] Record IEP character count, BIP character count, final prompt size, and removed boilerplate count.
- [x] Save a small extraction audit file for each case.
- [ ] Manually spot-check cleaned text before the full AWS runs.

## 3. Strengthen Ground Truth

- [x] Add ground-truth audit helpers for each field.
- [x] For true fields, point to source pattern hits when the deterministic rules find them.
- [x] For false fields, flag whether risky template language was removed.
- [x] Make special notes for fields where template language appears but the student-specific fact is false.
- [x] Add this especially for restraint/isolation, staffing ratios, services, functions, and accommodations.
- [x] Make ground truth easier to audit without opening the full IEP/BIP every time.
- [ ] Manually review any field marked `needs_manual_note_true_field` or `needs_manual_review_false_field`.

## 4. Tighten Scoring Rules

- [x] Review high-risk scoring fields.
- [x] Add positive examples for the most important fields.
- [x] Add false-positive examples for the riskiest fields.
- [x] Fix high-risk terms like `isolation`, `restraint`, `attention`, `sensory`, and `support`.
- [x] Make the scoring distinguish between template language and student-specific claims better than before.
- [x] Add unit tests for common false positives.
- [x] Add unit tests for common model phrasing.
- [x] Keep saving positive hits, negative hits, and matched patterns for every field.
- [ ] Review missed fields after the next pilot run and tighten anything still suspicious.

## 5. Separate Error Types

- [x] Keep overall accuracy, but add clearer error categories.
- [x] Add `correct_present`.
- [x] Add `correct_absent`.
- [x] Add `omission`.
- [x] Add `unsupported_addition`.
- [x] Add `wrong_negative`.
- [x] Make result summaries show what kind of mistake happened, not just whether it was wrong.

## 6. Improve Claim Extraction

- [x] Keep the deterministic claim splitter for now.
- [x] Add a simple evidence-checking step for extracted claims.
- [x] Mark claims as `supported`, `unsupported`, or `unclear`.
- [x] Do not call it unsupported-claim rate until evidence checking exists.
- [x] Start with document text matching before using any LLM judge.
- [x] Save claim evidence in the output folder.
- [ ] Review claim support quality after the next pilot run.

## 7. Validate Case Variability

- [x] Check which fields are true and false across selected cases.
- [x] Save a case-set audit file with never-true fields.
- [ ] Decide whether never-true fields are intentional hallucination stress tests.
- [ ] Decide if more cases are needed for positive examples.
- [ ] Specifically review self-injury, sensory function, safety plan, restraint/isolation, 1:1 ratio, and 2:1 ratio.
- [x] Write a short note explaining what the current case set can and cannot measure.

## 8. Run A Small Pilot Before Full Runs

- [ ] Pick 2-3 representative cases.
- [ ] Run the pilot cases on selected models only.
- [ ] Manually inspect every miss from the pilot.
- [ ] Separate model mistakes from scoring-rule mistakes.
- [ ] Fix scoring/extraction problems before full runs.
- [ ] Only run all 10 cases after the pilot looks defensible.

## 9. Choose Models With A Clear Reason

- [ ] Pick models by purpose, not randomly.
- [ ] Include a cheap baseline model.
- [ ] Include a mid-tier model.
- [ ] Include a stronger reasoning model.
- [ ] Include local models only if they are part of the comparison.
- [ ] Write down why each model was selected.
- [ ] Start with Nova Micro, Nova Lite, and Nova Pro for AWS scouting.

## 10. Improve Run Metadata

- [x] Save provider, model ID, AWS region, temperature, and max tokens.
- [x] Save prompt hash, case hash, script hash, and scoring-rule hash.
- [x] Capture Bedrock token usage if available.
- [ ] Add estimated cost per run if possible.
- [x] Keep Bedrock runs separate from LM Studio runs.
- [x] Keep run folders reproducible and easy to inspect.

## 11. Build A Results Review Workflow

- [x] Generate a review checklist after each run.
- [x] Show top missed fields.
- [x] Show likely false positives.
- [x] Show likely omissions.
- [x] Save raw response.
- [x] Save predicted JSON.
- [x] Save extracted claims.
- [x] Save field-level evidence hits.

## 12. Add Human Reliability Check

- [ ] Manually re-score a small sample after some time has passed.
- [ ] Record whether the second score matches the first score.
- [ ] If possible, have another person review a small sample later.
- [ ] Report agreement if we have enough time.
- [ ] Use this to defend against subjective grading concerns.

## 13. Update Documentation

- [x] Update the testing protocol.
- [ ] Update development notes as changes are made.
- [x] Add a short limitations section.
- [x] Mention synthetic cases.
- [x] Mention deterministic scoring.
- [x] Mention regex limitations.
- [x] Mention boilerplate risk.
- [x] Mention that there is no real student data.
- [x] Mention that claim evidence checking is still developing.

## 14. Final Pre-Run Checklist

- [ ] `validate` passes.
- [ ] Tests pass.
- [ ] Extraction audit looks clean.
- [ ] Ground truth has evidence notes.
- [ ] Scoring rules have false-positive tests.
- [ ] Pilot results were manually reviewed.
- [ ] AWS budget alert is confirmed.
- [ ] Model list is locked.
- [ ] Run IDs are planned.
- [ ] No private/licensed files are being pushed to GitHub.

## Current Priority

Start here:

1. Review the cleaned text from `hardening_extract_check`.
2. Run one small AWS Bedrock pilot.
3. Inspect `review_checklist.md`, `ground_truth_audits`, and `claims`.
4. Tighten any scoring rule that looks wrong.
5. Full test runs only after the pilot looks defensible.
