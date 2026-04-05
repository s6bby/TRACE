# Methodology Appendix

**Evaluating Claim-Level Reliability in Large Language Model Interpretation of Special Education Documents**

## Research Question

This project asks whether large language model outputs can be evaluated more reliably by breaking them into individual claims and checking whether each claim is supported by the source documents. The goal is to determine whether a claim-level approach makes unsupported statements easier to identify in high-stakes document interpretation.

## Why This Problem Matters

Special education documents such as Individualized Education Programs and Behavior Intervention Plans contain detailed, case-specific information that can affect how students are supported. If an AI system produces an unsupported interpretation of those documents, the result is not just a small technical error. It can change how educators, staff, or families understand a student's needs and services. That makes reliability and evidence traceability especially important in this setting.

## Method Overview

The project used a document-grounded evaluation process rather than a general judgment of output quality.

### 1. Document Selection and Preparation

I worked with special education document materials chosen to reflect the structure and complexity of IEPs and BIPs. The goal was to study how language models handled real document features such as dense case information, service descriptions, behavioral supports, and educational planning details.

### 2. Prompting and Response Collection

I used structured prompts to generate model outputs that summarized, interpreted, or answered questions about the documents. This created a set of responses that could be compared against the original source material.

### 3. Claim-Level Decomposition

Instead of evaluating a model response as one overall answer, I broke the response into individual claims. Each claim was treated as a separate statement that could be checked against the document.

### 4. Evidence Comparison

Each claim was compared to the source record to determine whether it was grounded in the document. This made it possible to study reliability at the level of specific statements rather than general impressions.

### 5. Support Classification

Claims were organized into three categories:

- `Explicitly supported`: directly stated in the source document
- `Reasonably inferred`: not stated word-for-word, but supported by the available evidence
- `Unsupported`: not justified by the source material

### 6. Pattern Analysis

After classifying the claims, I examined how unsupported claims appeared across model outputs. This helped reveal whether the models tended to overstate, extend, or blend information beyond what the documents actually supported.

## Core Methodological Contribution

The main contribution of this project is a shift in how reliability is evaluated. Instead of asking whether an answer seems good overall, this method asks whether each part of the answer can be justified by evidence. That makes model behavior easier to inspect and produces a clearer distinction between valid interpretation and unsupported content.

## My Role

My role in this project included defining the research question, developing the claim-level evaluation framing, organizing the document-grounded analysis approach, and analyzing how unsupported claims appeared in model outputs. I was responsible for helping turn a general concern about AI accuracy into a more structured method for evaluating reliability through evidence and traceability.

## Key Takeaway

This methodology showed that fluent AI outputs can still contain unsupported claims that are easy to miss without structured review. By evaluating responses at the claim level, the project made those reliability failures more visible and easier to analyze.
