# Meeting Prep: Fellowship, Reliability Research, and Next Steps

## What Ben's Email Means

Ben's message is a positive signal. He is saying there is a plausible path from your fellowship work to:

1. summer research output
2. a small publication such as a workshop or conference-adjacent venue
3. a later grant proposal built on those early results

He is not saying funding is guaranteed. He is saying your project may be strong enough to produce:

- preliminary results this summer
- a publishable paper or workshop submission
- a stronger case for external funding after that

Important translation of the key terms:

- `RFP`: Request for Proposals. This is the formal document describing what a grant program wants to fund.
- `preliminary results`: early evidence that your idea works well enough to justify a larger project
- `workshop or conference-lite venue`: a smaller or more specialized publication venue that is realistic for an early-stage project
- `publication as a springboard`: use a paper to show feasibility, then use that paper to support a grant proposal

## What "Reliability" Likely Means in This Meeting

For your project, reliability does not mean "the model sounds good." It means:

- whether a claim is actually supported by source evidence
- whether the system separates direct evidence from inference
- whether unsupported statements can be caught before being presented as fact
- whether a human can inspect why the system produced a judgment

Your strongest framing is:

`TRACE is a claim-level reliability and interpretability framework for document-grounded LLM outputs in high-stakes settings.`

That is a better research framing than:

- "an AI tool for special education"
- "a chatbot for IEPs"
- "a general summarizer"

Special education should be presented as the first domain and testbed, not the only reason the work matters.

## How to Bridge Your Project to Xinghui Zhao's Research Context

Professor Zhao's published WSU research profile emphasizes:

- parallel and distributed systems
- big data analytics
- machine learning
- cloud computing
- interdisciplinary AI work on real-world problems

That means you should frame your work so it sounds like a serious computing research problem, not only a personal or application-specific project.

Good bridge language:

- "I am studying reliability in AI-assisted document interpretation."
- "The core problem is evidence-grounded validation of model outputs."
- "Special education is the initial high-stakes evaluation domain, but the framework is meant to generalize."
- "The technical contribution is claim decomposition, evidence retrieval, constrained evaluation, and deterministic validation."

## Your Core 30-Second Explanation

`My project studies whether we can make LLM outputs more reliable in high-stakes document settings by validating them at the claim level instead of trusting the response as a whole. The system breaks an answer into claims, finds supporting evidence in the source documents, and labels each claim as explicit, inferred, or unsupported. Special education documents are the first test domain, but the broader research question is how to make AI outputs traceable, auditable, and safer in real-world use.`

## What You Should Be Ready to Say in the Meeting

### 1. The research question

Be ready to say:

`The main research question is whether a claim-level validation framework can reduce unsupported statements and improve evidence traceability in LLM outputs.`

### 2. Why this is research and not just a product

Be ready to say:

- you are comparing baseline outputs against validated outputs
- you have measurable outcomes
- you are studying failure modes
- you are testing a framework, not just building an app

### 3. Why special education is the first domain

Be ready to say:

- it is a high-stakes setting
- documents are complex and structured
- errors matter
- it provides a strong real-world testbed for reliability research

Then add:

`I am using special education as the initial domain, but the framework is meant to generalize to other document-grounded settings.`

### 4. What you can realistically finish this summer

A credible summer scope:

- define claim schema and support labels
- build a small case set using synthetic, sanitized, or de-identified materials
- collect baseline outputs from 2 to 4 models
- implement a first-pass pipeline for claim extraction, evidence matching, and validation
- produce preliminary metrics and a few analyzed examples

### 5. What counts as preliminary results

You do not need a finished platform. Preliminary results could be:

- a small benchmark set
- examples showing unsupported claims in baseline outputs
- early evidence that the validation framework improves traceability
- quantitative patterns such as lower unsupported-claim rate or better evidence coverage

### 6. What publication path makes sense

The right first publication is probably not a top-tier major conference paper. A more realistic target is:

- a workshop paper
- a student research symposium paper/poster
- a regional or specialized computing/AI venue

That is consistent with what Ben said.

## Questions They Are Likely to Ask

You should have short answers ready for these:

1. What exactly is the contribution?
   The contribution is a framework for claim-level reliability evaluation of document-grounded LLM outputs.

2. What is novel here?
   The project focuses on claim-level justification and evidence traceability rather than a single overall quality judgment.

3. What data will you use?
   Synthetic, sanitized, or de-identified IEP/BIP-like materials for repeated testing.

4. How will you evaluate success?
   Unsupported-claim rate, evidence traceability coverage, claim label distribution, and qualitative failure analysis.

5. What are the risks?
   Claim extraction errors, retrieval misses, evaluator drift, and overconfidence in the report.

6. How is this broader than special education?
   The framework is domain-portable for other high-stakes document settings if the evidence hierarchy is preserved.

7. What do you need from faculty support?
   Research framing, publication strategy, feedback on methodology, and alignment with any grant RFP requirements.

## What You Should Know Before the Meeting

Do not overclaim:

- TRACE does not prove truth.
- TRACE does not replace human review.
- TRACE does not guarantee correctness.
- TRACE is a reliability support framework, not an autonomous decision-maker.

Do emphasize:

- evidence traceability
- interpretability
- measurable evaluation
- model-agnostic design
- high-stakes document reliability

## Documents You Should Send Ben

Send a small, focused packet. The best set is:

1. your fellowship answers
2. your TRACE abstract and methods documents
3. a one-page research summary tailored for this meeting

If you have them, also send:

4. a short SURCA summary with any existing results, screenshots, or examples
5. a short list of open research questions or proposed summer milestones

If you do not yet have a SURCA summary, do not delay the meeting. Send the first three documents now.

## Recommended Attachment Order

Use these files:

1. `applications/wsuv-fellowship-application-responses.md`
2. `abstracts/trace-v1-project-abstract.md`
3. `abstracts/trace-one-page-summary.md`

## What the One-Page Summary Should Contain

Keep it tight:

- project title
- one-sentence research question
- 3 to 4 sentence project summary
- summer deliverables
- evaluation metrics
- publication goal
- future grant relevance

## Short Email Draft

Subject: Materials for our fellowship and summer research meeting

Hi Dr. McCamish,

I wanted to send over a few materials ahead of our meeting with Professor Zhao. I attached my current fellowship responses, the TRACE project abstract, and a short summary of the research direction and planned summer scope.

The central research focus is claim-level reliability for document-grounded LLM outputs: identifying whether model-generated claims are explicitly supported, inferred, or unsupported based on source evidence. I framed special education as the initial high-stakes domain, while keeping the broader contribution centered on AI reliability, traceability, and interpretability.

I thought these might be useful for shaping the summer work and for aligning it with the RFP once it arrives.

Best,
Sebastian

## Best Meeting Posture

Go into the meeting as someone who already has a research direction, but is open to narrowing and reframing it. Your goal is not to defend every current detail. Your goal is to show:

- the project is researchable
- the scope can be made realistic
- the work can produce preliminary results
- the framing can support publication and later funding

## Sources

- WSU Vancouver directory for Xinghui Zhao: https://directory.vancouver.wsu.edu/people/xinghui-zhao
- WSU Vancouver faculty research page: https://ecs.vancouver.wsu.edu/faculty-research
- WSU REU team page mentioning interdisciplinary AI and machine learning work: https://reu.encs.vancouver.wsu.edu/team/
