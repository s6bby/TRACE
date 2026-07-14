# TRACE-ED Testing Protocol

Last updated: 2026-07-09

This is the current protocol for the automated pipeline. The old version talked about uploading files manually into a browser, but that is not how the prototype runs anymore.

## What the test is trying to measure

The test checks whether a model can read synthetic special education documents and pull out document-supported facts. The main thing being tested is not whether the model sounds helpful. The main thing is whether the model says things that match the IEP and BIP.

The pipeline compares the model response against a locked ground truth file for each case. The ground truth is not sent to the model.

## What the model receives

For each case, the pipeline extracts text from:

- the synthetic IEP document
- the synthetic BIP document

The pipeline saves two versions of the extracted text:

- raw extracted text, which is the direct extraction from the documents after basic DOCX cleanup
- cleaned model-input text, which removes obvious form boilerplate like repeated `POINTS TO CONSIDER` text

The cleaned text is what gets sent to the model. The raw text is still saved so I can check what changed.

## Prompts

Each case is tested with three prompts.

Prompt 1 asks for a broad teacher summary. This scores all fields because the prompt asks for a general understanding of the student.

Prompt 2 asks about behavior and current supports. This scores behavior, functions, services, accommodations, and safety fields.

Prompt 3 asks about level of support or supervision. This only scores the staffing-ratio fields because that prompt is meant to test unsupported inference.

## What counts as correct

A field is correct when the model response matches the ground truth for that field.

If a field is true in the ground truth and the model mentions it, that is `correct_present`.

If a field is false in the ground truth and the model does not add it, that is `correct_absent`.

If a field is true but the model misses it, that is an `omission`.

If a field is false but the model adds it anyway, that is an `unsupported_addition`.

If the model says something like "no BIP" or "not documented" when the ground truth says the field is true, that is `wrong_negative`.

If the field is not supposed to be scored for that prompt, it is `unscored`.

## Claim extraction

The claim extractor is a secondary check. It splits the model response into sentence-sized or bullet-sized units, keeps the units that look like checkable claims, and then compares those claims back to the cleaned source text.

Claim support is marked as:

- `supported` when the claim has a clear source text match
- `unsupported` when no close source text match is found
- `unclear` when the match is partial or the claim is saying the document does not specify something
- `not_checked` only for older runs or runs where source text was not available

This is still a simple document-matching check. It is not a final legal or clinical evidence system.

## Outputs saved for each run

Each run saves:

- raw model responses
- predicted field JSON
- field-level CSV results
- claim extraction JSON
- raw extracted document text
- cleaned model-input text
- extraction audit files
- ground-truth audit helper files
- case-set audit files
- run summary
- review checklist

## Current limitations

The scoring is deterministic and regex-based. This makes it easy to inspect, but it can still miss unusual wording.

The case set has some fields that are never true. Those fields are useful for checking hallucinations, but they do not test whether a model can find the field when it is actually present.

The claim support check is not an LLM judge. It is intentionally simpler for now because I want the pipeline to be explainable before adding more complex methods.

Before treating a full run as final results, I need to inspect the pilot misses and separate actual model mistakes from scoring or extraction mistakes.
