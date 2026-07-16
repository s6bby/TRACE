# TRACE-ED Development Notes For Meeting

These are the notes I want available when I explain what has changed recently. The main point is that the project moved from "it runs" to "I can inspect what happened."

## Recent Pipeline Work

The biggest change was tightening the pipeline before collecting larger results. I did not want to start making tables if the text extraction or scoring was still too loose.

The pipeline now saves raw extracted text and cleaned text separately. That matters because the raw text shows what came out of the document, while the cleaned text shows what the model actually saw. If a model misses something, I can check whether the information was actually present in the model input.

The cleaner also removes more template language. Some of the IEP/BIP forms have repeated form text that is not really part of the case. If that goes into the model prompt, the model can get distracted or pick up details that are not case-specific. The point is not to hide information from the model. The point is to give it the actual case facts instead of a huge amount of repeated boilerplate.

## Scoring Changes

The scoring is now easier to defend because it does not only say correct or wrong. It separates different kinds of errors:

- `correct_present` means the model included something that should be there.
- `correct_absent` means the model did not invent something that should not be there.
- `omission` means the model missed something expected.
- `unsupported_addition` means the model added something that was not supported by the case text.

That last category is important because hallucination in this project is not just "weird answer." It can mean the model says a student has a support, service, behavior, or staffing detail that the documents do not actually support.

## Claim Work

The claim extraction is still early, but it is useful already. Instead of only looking at a whole response, the pipeline now breaks parts of the response into smaller claims and labels them as supported, unsupported, or unclear based on the cleaned source text.

This is not a perfect evidence checker yet. It is a first pass. The value right now is that it gives me a place to look when a model writes a fluent paragraph that may or may not be faithful to the documents.

## AWS / Local Separation

The project can now run through LM Studio locally or AWS Bedrock. AWS results go into a separate Bedrock output path, and the demo export can filter down to Bedrock-only results. This keeps old local runs, smoke tests, failed runs, and real AWS runs from getting mixed together.

The demo export now also has a minimum evaluation filter. For the meeting, the demo is using 30 evaluations as the cutoff, so only full 10-case runs show up.

## Current Result Collection

The current clean Bedrock set has six full runs:

- Nova Micro
- Nova Lite
- Nova Pro
- Llama 3.3 70B
- Mistral Large 3
- GPT OSS 20B

Each one ran all 10 cases with 3 prompts per case. That gives 30 evaluations per model.

## What I Need To Be Careful About

The numbers are useful, but I should not oversell them. A higher score does not automatically mean a model is safe. A lower score does not automatically mean a model is useless.

The better explanation is that the pipeline is now strong enough to start comparing model behavior under a controlled setup. The next step is spot-checking samples from the run folders so I can make sure the scores match what a person would see when reading the model responses.

## Demo Plan

For the meeting, I should show:

- the result summary first, so the overall picture is clear
- one run folder, so the professor can see the artifacts
- `field_results.csv`, because that shows the scoring at the field level
- the extracted/cleaned text, because that shows what the model actually saw
- the claim output, because that shows where evidence checking is going
- the demo UI last, because it is just a readable display, not the actual research method

My main line should be simple: TRACE-ED is a prototype for checking whether model answers stay grounded in special education-style documents.
