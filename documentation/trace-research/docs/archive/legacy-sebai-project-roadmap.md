# SebAI: Project Abstract and Roadmap

## Abstract

Large language models (LLMs) are increasingly used to interpret documents and assist with decision-making, but in high-stakes settings they often produce fluent responses that blur the boundary between what is directly supported, what is reasonably inferred, and what is simply unsupported. SebAI is an early-stage reliability framework designed to make that boundary visible. Rather than treating an AI response as a single unit to be rated for overall quality, SebAI decomposes the response into individual claims and evaluates whether each claim can actually be justified by available evidence.

In its first version, SebAI operates as a model-agnostic, post-response evaluation system. A user provides source document(s), the prompt used, and an LLM-generated response. SebAI then extracts structured claims, retrieves relevant evidence from the uploaded documents, and evaluates each claim through a hybrid architecture that combines constrained AI-based reasoning with deterministic validation rules. Claims are classified as explicitly supported, inferred, or unsupported, and the system returns a structured reliability report containing evidence links, review priority, and explanatory notes. This approach is designed to improve traceability and interpretability rather than to generate a misleading single confidence score.

The initial research domain is special education, especially Individualized Education Programs (IEPs) and Behavior Intervention Plans (BIPs), where inaccurate interpretation can have direct consequences for students and staff. Within this setting, SebAI serves both as a research framework and as a working prototype for justification-constrained AI: a model in which outputs are judged not only by what they say, but by what they can justify. The long-term significance of the project is not limited to special education. If successful, the same framework can be extended to other high-stakes domains, including healthcare, legal reasoning, and compliance, and later expanded to incorporate curated scholarly or policy sources without allowing general domain knowledge to override case-specific facts.

## Project Definition

SebAI is not a new foundation model, a fine-tuning project, or a general chatbot. It is a reliability and interpretability framework that evaluates whether an existing LLM response is justified by evidence.

The deeper research direction is to shift AI evaluation from probability-driven output quality toward justification-constrained output validity. In practical terms, this means modeling:

- what the system can explicitly justify from evidence
- what the system can reasonably infer from evidence
- what the system cannot justify and should not present as fact

This makes SebAI more than a response checker. It is an attempt to represent the epistemic structure of an LLM output in a form that humans can inspect.

## Core Research Questions

1. Can a claim-level validation framework reduce unsupported statements in LLM outputs for high-stakes document interpretation?
2. How effectively can a hybrid AI-deterministic evaluation system distinguish between explicit support, inference, and lack of support?
3. Does claim-level reliability modeling improve evidence traceability and interpretability compared with raw LLM responses?
4. Can a post-response evaluator remain model-agnostic while still producing useful reliability reports across different LLMs?

## V1 Scope

### Included

- post-response evaluation of LLM outputs
- document-grounded verification using uploaded source material
- claim decomposition of model responses
- evidence retrieval from source documents
- claim classification as `explicit`, `inferred`, or `unsupported`
- deterministic validation rules that enforce traceability
- structured reliability reports for human review
- comparative evaluation across multiple LLM outputs
- special education as the primary test domain

### Not Included

- training or fine-tuning a new model
- replacing human review in high-stakes decisions
- guaranteeing correctness
- live autonomous generation of final answers in v1
- domain-general deployment across healthcare, legal, and compliance in v1
- unrestricted use of external knowledge as a source of truth

## Methodology

### 1. Domain and Case Preparation

SebAI v1 will be evaluated on synthetic, sanitized, or de-identified special education materials, with emphasis on IEPs and BIPs. The goal is to work with documents that preserve structural complexity without introducing unnecessary privacy risk. Cases should be standardized enough to support repeated testing across prompts and models.

Key tasks:

- define a document preprocessing pipeline
- normalize text and preserve meaningful sections
- create a structured case set for repeated evaluation
- document assumptions and edge cases

### 2. Baseline Response Collection

For each case, the same prompt or set of prompts will be submitted to multiple LLMs or paired with pasted outputs from multiple LLM systems. This produces a baseline set of unvalidated responses for comparison.

Key tasks:

- record prompt text and model metadata when available
- retain full raw response text before any processing
- use repeated prompt structures to support cross-model comparison

### 3. Claim Decomposition

Each response will be decomposed into discrete claims. This step is foundational because unreliable claim extraction will weaken the rest of the pipeline.

Recommended approach:

- use LLM-assisted extraction into a strict schema
- validate output format deterministically
- split compound statements when possible
- treat ambiguous or mixed claims as a known error source to analyze

Critical note:

Claim decomposition is itself a research risk. If the system merges multiple ideas into one claim or fragments one idea into many small claims, downstream support labels may become unstable. This stage should be evaluated explicitly, not treated as a solved preprocessing step.

### 4. Evidence Retrieval

For each claim, SebAI retrieves relevant evidence snippets from the uploaded document set. V1 should favor hybrid retrieval over a purely semantic or purely lexical approach.

Recommended retrieval strategy:

- semantic retrieval for paraphrased matches
- keyword or lexical retrieval for exact terminology
- top-k candidate evidence spans for downstream comparison

Critical note:

Retrieval failure can masquerade as reasoning failure. If the correct evidence is never surfaced, a supported claim may be mislabeled as unsupported. Retrieval performance should therefore be treated as a separate point of analysis.

### 5. AI Evaluation Layer

An evaluator model reviews each claim together with candidate evidence and assigns a provisional label:

- `explicit`: directly supported by the document
- `inferred`: not directly stated, but reasonably derived from the evidence
- `unsupported`: not justified by the evidence provided

The evaluator should not operate as a second free-form chatbot. Its role is a constrained reasoning function working inside a strict schema.

Recommended controls:

- require structured outputs
- require evidence citation for every non-unsupported claim
- separate label selection from explanatory note generation
- keep prompts narrow and task-specific

### 6. Deterministic Validation Layer

A deterministic layer checks whether the evaluator output obeys the system's reliability rules.

Core rules:

- every supported or inferred claim must be linked to evidence
- evidence snippets must correspond to real text from the document
- unsupported claims must be clearly flagged
- claims with weak evidence should receive elevated review priority
- unsupported information should not be blended into factual summaries without clear labeling

This layer is essential because SebAI does not assume the evaluator is trustworthy by default.

### 7. Reliability Modeling and Reporting

Instead of producing a single confidence score, SebAI returns a structured reliability profile.

Expected output fields:

- claim text
- evidence snippets
- support type
- review priority
- notes on ambiguity, missing information, or conflict

This enables a human reviewer to see not only whether a response contains problems, but where those problems are concentrated and why.

## Evaluation Strategy

### Primary Evaluation Target

The main goal is not simply hallucination reduction. The primary research target is improved evidence traceability and interpretability of LLM outputs.

### Secondary Outcomes

- reduction in unsupported claims
- clearer separation between fact and inference
- better visibility into model failure patterns
- improved usefulness for human review in high-stakes workflows

### Core Metrics

- proportion of claims labeled explicit
- proportion of claims labeled inferred
- proportion of claims labeled unsupported
- evidence traceability coverage
- rate of claims with missing or weak evidence
- distribution of review priority labels

### Comparative Conditions

- raw LLM response without SebAI analysis
- SebAI-processed reliability report for the same response
- cross-model comparison on identical prompts and case materials

### Qualitative Analysis

Quantitative metrics alone are not sufficient. Peer review of selected cases should examine:

- whether claims were extracted at the right level of granularity
- whether retrieved evidence was actually the best available support
- whether the distinction between explicit and inferred is consistent
- which failure patterns recur across models or prompts

## Threats to Validity and Design Risks

### Claim Boundary Instability

The meaning of a result depends on how a response is segmented into claims. Poor decomposition can distort all downstream labels.

### Retrieval Misses

A correct claim may appear unsupported if the retrieval layer fails to surface the right evidence.

### Evaluator Drift

The evaluator model may over-accept weak evidence or over-penalize reasonable inference. Deterministic checks reduce this risk but do not eliminate it.

### False Sense of Security

A polished reliability report could be mistaken for proof of correctness. SebAI should be presented as a decision-support tool, not an oracle.

### Source Hierarchy Confusion

When future versions introduce scholarly or policy sources, the system must preserve a clear hierarchy:

- case-specific documents remain authoritative for case facts
- domain sources provide context, norms, or general guidance
- conflicts must be surfaced rather than silently resolved

## Roadmap

### Phase 1: Research Framing and Schema Design

Goals:

- finalize research questions
- define the claim schema and report schema
- define source hierarchy and validation rules
- document v1 non-goals to control scope

Deliverables:

- claim schema
- support label definitions
- reliability report format
- methodology notes

### Phase 2: Data Preparation and Baseline Collection

Goals:

- assemble structured test cases
- define prompt sets
- gather baseline outputs from multiple models

Deliverables:

- case corpus
- prompt set
- raw model output set

### Phase 3: Core Pipeline Implementation

Goals:

- implement claim decomposition
- implement evidence retrieval
- implement evaluator prompts and strict schemas
- implement deterministic validation

Deliverables:

- working backend pipeline
- structured evaluation objects
- error logging for failure analysis

### Phase 4: Reliability Reporting Prototype

Goals:

- build a lightweight interface for uploading documents and responses
- display claim-by-claim evidence support
- expose review priority and notes clearly

Deliverables:

- prototype interface
- human-readable reliability report

### Phase 5: Evaluation and Iteration

Goals:

- measure claim support distributions
- test traceability and interpretability outcomes
- analyze recurring failure patterns
- refine retrieval and validation rules based on results

Deliverables:

- comparative evaluation results
- failure analysis summary
- revised pipeline design

### Phase 6: Dissemination and Future Design

Goals:

- prepare peer-facing materials
- present results in undergraduate research settings
- formalize next-step architecture for scholarly-source integration

Deliverables:

- poster or presentation
- written report
- future-scope design brief

## Future Scope Beyond V1

The most important planned expansion is the addition of curated scholarly, policy, or domain-reference sources. This should not be framed as a generic retrieval add-on. It creates a second knowledge layer with a distinct role.

In later versions, SebAI should distinguish between:

- document-grounded truth: case-specific facts and requirements
- domain-grounded knowledge: broader scholarly, policy, or normative guidance

This opens a more advanced research direction:

- evaluating whether a claim is justified by the case record
- evaluating whether a recommendation aligns with established domain knowledge
- surfacing conflicts between case documents and general guidance

The key design rule is that external knowledge must contextualize or challenge interpretation without silently overriding case-specific evidence.

## Recommended Technical Stack for V1

- `Python` for research iteration and NLP tooling
- `FastAPI` for the backend API
- `Pydantic` for strict schemas
- `sentence-transformers` plus lexical retrieval for hybrid evidence search
- `FAISS` or `Chroma` for retrieval indexing
- `python-docx` and `pymupdf` for document ingestion
- `React`, `TypeScript`, and `Vite` for a lightweight interface

## Non-Goals and Guardrails

- SebAI should not be described as proving truth.
- SebAI should not collapse explicit evidence and inference into a single confidence score.
- SebAI should not hide uncertainty in the name of cleaner output.
- SebAI should not treat the evaluator LLM as authoritative without checks.
- SebAI should not expand into too many domains during v1.

## Working Thesis

SebAI is an early-stage framework for justification-constrained AI that models what parts of an LLM response are explicitly supported, reasonably inferred, or unsupported, and makes that structure visible for human review.
