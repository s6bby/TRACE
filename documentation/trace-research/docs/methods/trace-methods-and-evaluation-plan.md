# TRACE Methods and Evaluation Plan

## Title

TRACE: Methods, Framework Design, and Results Collection Plan

## Overview

TRACE is a post-response reliability framework for evaluating whether the claims in a large language model output are justified by source evidence. The central methodological shift is from evaluating an answer as a single unit to evaluating it as a set of discrete, inspectable claims. This makes reliability a question of evidence-grounded justification rather than surface quality alone.

## Framework Logic

TRACE operates on three core distinctions:

- what a response can explicitly justify from the source documents
- what a response can reasonably infer from the source documents
- what a response cannot justify and should not present as fact

This means the framework is designed to model the epistemic structure of an output, not simply to rate whether it "looks good."

## Method Summary

TRACE v1 consists of six major stages:

1. case preparation
2. baseline response collection
3. claim decomposition
4. evidence retrieval
5. constrained claim evaluation
6. deterministic validation and reporting

## 1. Case Preparation

The evaluation set will consist of synthetic, sanitized, or de-identified special education materials, with emphasis on IEPs and BIPs. The goal is to preserve the structural and interpretive difficulty of the domain while minimizing privacy risk.

### Required preparation steps

- standardize source documents into a consistent text-processing format
- preserve section boundaries, headings, and key contextual fields
- document any assumptions made during preprocessing
- create repeated case packages that can be used across models and prompts

### Why this matters

If the source materials are inconsistent or poorly structured, later failures in retrieval or claim support may reflect preprocessing problems rather than model behavior.

## 2. Baseline Response Collection

For each case, the same prompt set will be used to generate outputs from multiple LLMs or multiple system conditions. These raw outputs serve as the baseline condition against which TRACE analysis will be compared.

### Collection rules

- preserve the exact prompt text for every run
- record model name and available metadata
- retain the full raw output before any transformation
- use repeated prompt templates to support fair comparison

### Example task types

- summarize the case
- identify supports or interventions
- explain major concerns in the document
- answer case-specific questions grounded in the record

## 3. Claim Decomposition

Each model response will be segmented into discrete claims. A claim is a unit of meaning that can be evaluated against source evidence.

### Claim decomposition strategy

- use a constrained LLM step to extract claims into a strict schema
- split compound statements when feasible
- retain a link from each claim back to the original response span
- validate structure deterministically before downstream use

### Core schema fields

- claim identifier
- claim text
- source response span
- claim type if needed for analysis
- ambiguity flag when segmentation is unstable

### Research risk

Claim decomposition is not a trivial preprocessing step. Over-merging claims can hide unsupported content, while over-splitting can distort the evaluation. TRACE therefore treats claim-boundary instability as a methodological concern to be studied explicitly.

## 4. Evidence Retrieval

For each claim, TRACE retrieves candidate evidence spans from the source documents. The retrieval layer should combine semantic and lexical methods to avoid over-reliance on paraphrase or exact wording alone.

### Retrieval approach

- semantic retrieval for paraphrased or conceptually similar passages
- lexical or keyword retrieval for direct terminology matches
- top-k evidence candidates retained for downstream evaluation

### Retrieval outputs

- evidence snippet text
- document section or location metadata
- retrieval score or ranking information if available

### Research risk

Retrieval failure can be mistaken for reasoning failure. A supported claim may appear unsupported if the right evidence is never surfaced. For that reason, retrieval quality should be analyzed separately from claim-label accuracy.

## 5. Constrained Claim Evaluation

An evaluator model will review each claim together with candidate evidence spans and assign a provisional support label.

### Support labels

- `explicit`: directly supported by the source text
- `inferred`: not directly stated, but reasonably derived from the available evidence
- `unsupported`: not justified by the evidence provided

### Evaluation constraints

- require structured outputs rather than free-form text
- require cited evidence for every `explicit` or `inferred` judgment
- separate label selection from explanatory note generation
- keep the evaluator prompt narrow and role-constrained

### Theoretical role of this layer

The evaluator is not treated as an authoritative judge. It is a constrained reasoning component whose outputs must still pass deterministic checks.

## 6. Deterministic Validation and Reliability Reporting

After the evaluator produces provisional judgments, TRACE applies rules that enforce traceability and consistency.

### Validation rules

- every non-unsupported claim must link to real evidence text
- evidence spans must correspond to text that exists in the source documents
- unsupported claims must remain visibly flagged
- weakly supported or ambiguous claims should receive higher review priority
- unsupported information should not be blended into factual reporting without clear labeling

### Reliability report fields

- claim text
- claim label
- supporting evidence spans
- rationale or note
- ambiguity indicator
- review priority

## How the Framework Works in Theory

TRACE is grounded in the idea that trustworthy AI output requires more than fluent generation. In high-stakes document settings, a useful system must show what parts of an answer are directly grounded, what parts depend on bounded inference, and what parts lack evidentiary support. The framework therefore treats reliability as a structured relationship between claims and evidence rather than as a generic confidence estimate.

This produces a more interpretable object for human review. Instead of asking whether a full paragraph is "correct," TRACE asks whether each individual proposition in that paragraph is justified and visible to inspection.

## Results Collection Plan

TRACE v1 will collect both quantitative and qualitative results.

### Quantitative results

- proportion of claims labeled `explicit`
- proportion of claims labeled `inferred`
- proportion of claims labeled `unsupported`
- evidence traceability coverage
- rate of claims with missing or weak evidence
- distribution of review priority labels

### Comparative conditions

- raw LLM outputs without TRACE analysis
- TRACE-processed analysis of the same outputs
- cross-model comparison on matched prompts and cases

### Qualitative analysis

Selected cases will be reviewed to examine:

- whether claim boundaries were set appropriately
- whether the retrieved evidence was the best available support
- whether `explicit` and `inferred` labels were applied consistently
- which failure patterns recur across models or prompts

## Threats to Validity

### Claim-boundary instability

Different segmentation choices can produce different downstream results.

### Retrieval misses

A supported claim may look unsupported because the relevant evidence was not retrieved.

### Evaluator drift

The evaluator may over-accept weak evidence or over-penalize reasonable inference.

### False confidence

A polished report may be mistaken for proof of correctness if the system is presented carelessly.

## Expected v1 Outcome

The goal of TRACE v1 is not to eliminate all model error. The goal is to determine whether claim-level reliability analysis can make document-grounded LLM outputs more traceable, more interpretable, and more useful for human review in a high-stakes domain.
