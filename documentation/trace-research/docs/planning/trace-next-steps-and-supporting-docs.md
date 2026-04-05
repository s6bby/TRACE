# TRACE Next Steps and Supporting Documentation

## Purpose

This document translates the TRACE research concept into immediate next steps for summer work, meeting preparation, and publication-oriented planning. It is designed to support conversations with faculty mentors, potential collaborators, and future grant or fellowship reviewers.

## Current Position

TRACE is currently best framed as an early-stage research framework rather than a finished software product. The immediate objective is to produce a well-scoped v1 study that yields preliminary but credible results.

That means the next phase should prioritize:

- formalizing the research framing
- narrowing the v1 scope
- assembling the evaluation materials
- implementing the minimum reliable pipeline
- producing analyzable results suitable for a workshop-style venue

## Immediate Priorities

### 1. Finalize project language

Standardize the project around the TRACE name and use a consistent subtitle:

`TRACE: A Claim-Level Reliability Framework for Document-Grounded LLM Outputs`

All future materials should describe TRACE as:

- a post-response evaluation framework
- a claim-level reliability system
- a model-agnostic approach to evidence-grounded validation

Avoid describing TRACE as:

- a chatbot
- a special education assistant
- a system that proves correctness

### 2. Define the v1 research package

Before implementation, the project should formally define:

- the exact research questions
- the v1 non-goals
- the support-label definitions
- the claim schema
- the reliability report schema
- the evaluation metrics

These definitions will make later implementation and write-up much easier.

### 3. Assemble the test-bed

The first concrete research asset should be a small, reusable case set.

This should include:

- synthetic, sanitized, or de-identified IEP and BIP style documents
- repeated prompt templates for each case
- a small collection of raw outputs from multiple LLMs
- notes about edge cases and ambiguous examples

### 4. Build the minimum viable pipeline

The initial implementation does not need to be a polished end-user application. It should instead support the core research workflow:

- ingest source documents
- capture a prompt and model response
- extract structured claims
- retrieve evidence candidates
- assign support labels under constraints
- generate a human-readable reliability report

### 5. Produce preliminary results

The first results package should be strong enough to support:

- a mentor discussion about publication direction
- a workshop or student research submission
- future refinement toward grant-aligned research

Preliminary results do not need to prove the full thesis. They need to show that the framework is coherent, measurable, and worth extending.

## Proposed Summer Work Plan

### Phase 1: Framing and schema design

Deliverables:

- finalized title and framing language
- claim schema
- support-label definitions
- reliability report format
- v1 non-goals and guardrails

### Phase 2: Data and baseline collection

Deliverables:

- case set
- repeated prompt set
- baseline model outputs
- run log with model metadata

### Phase 3: Core pipeline implementation

Deliverables:

- claim extraction module
- evidence retrieval module
- evaluator prompt and schema
- deterministic validation checks

### Phase 4: Analysis and write-up

Deliverables:

- preliminary metrics
- selected case analyses
- failure-pattern summary
- abstract or short paper draft

## Recommended Supporting Documents

For mentor meetings and early publication planning, the following packet is sufficient:

1. a project abstract
2. a methods and evaluation plan
3. a next-steps and deliverables memo
4. fellowship materials as supporting context

The current TRACE packet should therefore consist of:

1. `abstracts/trace-v1-project-abstract.md`
2. `methods/trace-methods-and-evaluation-plan.md`
3. `planning/trace-next-steps-and-supporting-docs.md`
4. `applications/wsuv-fellowship-application-responses.md`

## Recommended Meeting Questions

These are the most useful questions to bring to the next faculty meeting:

1. Is the current v1 scope narrow enough to produce publishable preliminary results?
2. Does special education remain the best initial test-bed for the first study?
3. What venue would be the most realistic target for a first workshop-style submission?
4. How should the project be shaped once the RFP arrives?
5. Which methodological risks should be prioritized in the first evaluation cycle?

## Publication-Oriented Framing

When discussing the project with faculty, use this positioning:

`TRACE studies whether claim-level validation can make document-grounded LLM outputs more reliable, more traceable, and more interpretable in high-stakes settings.`

That framing is stronger than:

- "an AI tool for special education"
- "a document summarizer"
- "a safer chatbot"

## Practical Next Actions

The next concrete actions after this document set are:

1. complete any remaining TRACE language cleanup in legacy materials
2. tighten the abstract and methods language into a paper-ready tone
3. define the exact schema for claims and labels
4. decide what counts as a case package and baseline run
5. assemble the first evaluation set
6. begin implementation of the minimum viable research pipeline

## Guardrails for the Next Phase

As the project becomes more formal, keep the following constraints explicit:

- TRACE should not be presented as proving truth
- TRACE should not replace human judgment in high-stakes settings
- TRACE should not reduce reliability to a single confidence score
- TRACE should not quietly mix unsupported content into factual reporting
- TRACE should not expand beyond a manageable v1 scope
