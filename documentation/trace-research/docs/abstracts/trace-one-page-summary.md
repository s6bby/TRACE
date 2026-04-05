# TRACE One-Page Research Summary

## Project Title

TRACE: A Claim-Level Reliability Framework for Document-Grounded LLM Outputs

## Core Research Question

Can a claim-level validation framework reduce unsupported statements and improve evidence traceability in large language model outputs for high-stakes document interpretation?

## Project Summary

TRACE is an early-stage reliability and interpretability framework for evaluating whether large language model outputs are actually justified by source evidence. Instead of treating an AI response as a single unit, the system breaks the response into individual claims, retrieves relevant evidence from the source documents, and classifies each claim as `explicit`, `inferred`, or `unsupported`.

The initial research domain is special education, especially structured documents such as IEPs and BIPs, where inaccurate interpretation can have serious real-world consequences. This domain serves as the first high-stakes testbed, while the broader research contribution is a model-agnostic framework for evidence-grounded validation of AI outputs.

The technical goal is to combine claim decomposition, evidence retrieval, constrained LLM-based evaluation, and deterministic validation rules into a structured reliability report that supports human review.

## Summer Scope and Deliverables

Planned summer work:

- finalize the claim schema and support-label definitions
- build a small case set using synthetic, sanitized, or de-identified materials
- collect baseline outputs from multiple LLMs on repeated prompts
- implement a first-pass validation pipeline
- generate early comparative results and failure analysis

Expected deliverables:

- structured case set
- baseline output set
- working prototype pipeline
- preliminary reliability metrics
- short research report or workshop-style paper draft

## Evaluation Plan

The project will compare baseline LLM outputs against TRACE-validated analysis using:

- unsupported-claim rate
- evidence traceability coverage
- distribution of `explicit`, `inferred`, and `unsupported` labels
- qualitative analysis of recurring failure patterns

The main goal is not to "prove truth," but to improve traceability, interpretability, and visibility into model failure.

## Why This Matters

Current LLM systems often produce fluent but weakly justified claims. In high-stakes settings, that creates risk. TRACE investigates whether AI outputs can be made more auditable by requiring claim-level justification rather than relying on a single overall quality judgment.

Although the first application area is special education, the framework is intended to generalize to other document-grounded domains such as healthcare, legal reasoning, and compliance.

## Publication and Grant Relevance

The short-term goal is to produce preliminary results strong enough for a workshop paper, student research venue, or conference-adjacent publication. Those results can then support a future grant proposal by demonstrating feasibility, measurable outcomes, and a credible technical research direction.
