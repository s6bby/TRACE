# TRACE Literature Notes For Meeting

These are short notes from the papers I want to keep straight during the meeting. This is not written like a finished literature review yet. It is more of a working map of what each paper gives me.

## Voultsiou and Moussiades (2025)

This is the main special education background paper. It reviews AI, VR, AR, and LLM work in special education and talks about personalization, communication support, adaptive learning, teacher readiness, ethics, accessibility, and cost.

The useful part for TRACE is that it shows special education is already a real area for AI research, but also that the field is complicated. Students have different needs, and an AI tool that sounds helpful can still be wrong or misleading if it misunderstands the student context.

I would use this paper to explain why TRACE is focused on special education documents instead of generic chatbot questions. The weak part is that it is broad and does not give a technical claim-checking method.

## Sureshkumar et al. (2026)

This paper is more about an AI assistive learning system. It talks about machine learning, NLP, computer vision, emotion-aware tutoring, adaptive content, and dashboards.

I see it as a background paper, not a core technical one. It helps show what bigger education AI systems might look like, but TRACE is not trying to build a tutoring system right now. TRACE is more like a reliability check before systems like that should be trusted.

## Dougrez-Lewis et al. (2025)

This is one of the most important papers for the technical side. It looks at LLM claim verification and separates different kinds of reasoning. The big thing I took from it is that verifying a claim is harder than just asking whether something sounds true.

This connects directly to TRACE because model responses need to be broken into claims and checked against source documents. Whole-response scoring is useful, but claim-level checking is closer to what the project is trying to do.

The limitation is that their datasets are not special education records, so the paper supports the method direction more than the specific domain.

## Dmonte et al. (2024)

This is a survey of claim verification with LLMs. It lays out the larger workflow: detect claims, decide which claims matter, retrieve evidence, compare the evidence, make a judgment, and explain the judgment.

This helps me see where TRACE fits. TRACE-ED is still early. It extracts text, runs models, scores fields, and starts splitting claims. A later version of TRACE would need stronger evidence linking.

I would use this paper for roadmap framing more than for proving the current prototype.

## Kalai et al. (2026)

This paper is about hallucinations and why evaluation can reward guessing. The useful idea for TRACE is that abstention is not automatically bad. Sometimes the safer answer is "I cannot determine that from the documents."

This matters because I do not want the scoring to reward models for being confident when the source text does not support the answer. Unsupported claims should count against the model, and abstentions should be tracked separately.

## van Schaik and Pugh (2024)

This paper helped me think about the pipeline as a system, not just a model. It separates model evaluation from system evaluation and says different parts of a pipeline should be checked separately.

That maps well onto TRACE-ED because the project has several stages: extraction, cleaning, prompting, model response, scoring, claim splitting, and exporting. If something goes wrong, I need to know which part caused it.

I would use this paper to explain why the project saves so many artifacts. The artifacts are not clutter. They are what make the results inspectable.

## Malin et al. (2025)

This paper reviews faithfulness metrics. The useful part is that generated text can be fluent but still not faithful to the source. That is basically the TRACE problem.

The paper also supports breaking text into smaller facts or claims. A big paragraph is hard to inspect. Smaller claims are easier to compare against evidence.

The caution here is that no single metric works everywhere, and LLM evaluators can be helpful but unreliable.

## Fu et al. (2023)

This paper is a warning about using LLMs as judges. It tests whether models can reliably evaluate factuality and finds that the correlation with human judgment can be weak.

This is useful because it explains why I did not just ask another LLM to grade the responses. If I use an LLM judge later, it needs to be validated. It should not silently become the truth source.

## Bolli and Matta (2026)

This paper is about controls for high-stakes LLM systems. The useful parts are logging, traceability, evidence support, and constraints. That matches the direction TRACE is moving in.

I would not lean on this paper too hard because some parts feel less directly connected to special education, but it does support the general idea that high-stakes AI systems need audit trails.

## What These Papers Say Together

The papers point toward the same basic issue: AI tools are moving into sensitive areas, but evaluation is still messy. TRACE-ED is not trying to deploy AI in classrooms. It is trying to test whether model responses can be traced back to special education-style documents.

The main meeting takeaway is this: being helpful is not enough. If a model makes unsupported claims, it can still be misleading. That is why TRACE is moving toward claim-level checking and evidence support.
