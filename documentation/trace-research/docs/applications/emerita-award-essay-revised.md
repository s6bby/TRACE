# Emerita Award Supplemental Essay

## Revised Essay Draft

**Evaluating Claim-Level Reliability in Large Language Model Interpretation of Special Education Documents**

Large language models are becoming more common tools for summarizing documents and answering questions, but that does not mean their answers are reliable. My research grew out of that concern. I wanted to understand what happens when an LLM is used to interpret high-stakes documents and whether there is a clear way to check what the model says against the actual record. I focused on special education documents, especially Individualized Education Programs and Behavior Intervention Plans, because they are detailed, case-specific, and directly connected to decisions about student support. In that setting, an unsupported statement is not a small technical mistake. It can change how someone understands a student's needs, accommodations, or behavior plan.

The main question behind my project was straightforward: when a model gives an answer about a document, how much of that answer is actually supported by the source text? I found that this is harder to judge than it first appears. LLM outputs often sound fluent and organized even when they go beyond the evidence in the document. A response can mix directly supported facts, reasonable inferences, and unsupported claims in a way that is easy to miss if someone only reads the final answer and not the source material. That problem pushed me toward a claim-level approach instead of a general quality judgment.

My research focused on breaking model outputs into individual claims and then checking whether those claims could be justified by the underlying documents. Instead of treating a response as simply good or bad overall, I treated it as a set of smaller statements that could each be evaluated. I worked from special education document materials and used structured prompts designed to produce summaries, interpretations, and case-specific responses. I then compared the model's statements to the source record and organized them into three categories: claims that were explicitly supported, claims that could reasonably be inferred, and claims that were unsupported.

This method mattered because it exposed a kind of failure that is easy to miss in ordinary use. A model can sound confident, coherent, and helpful while still overstating what the document actually says. The most important pattern I found was not that the models were useless. It was that they could be genuinely helpful and still introduce unsupported information. That is a more serious reliability problem than a clearly wrong answer, because a polished answer can make readers less likely to question it. My results showed that unsupported claims were not rare exceptions. They were a recurring issue that became much easier to see once the response was broken down and checked at the claim level.

The project also led me to think about reliability in a more technical way. I was not interested only in whether an answer seemed persuasive. I wanted a way to evaluate whether each part of the answer could be traced back to evidence. That is what led me to the claim-level validation approach that now anchors my continuing work. The framework separates what is directly grounded in the document from what is inferred and from what should not be presented as fact at all. In practical terms, that means treating AI reliability as an evidence and traceability problem rather than a matter of intuition.

The significance of this research is both immediate and broader in scope. In the immediate sense, it addresses a real problem in special education document interpretation, where unsupported claims could affect how people understand student services and interventions. More broadly, the same issue appears in other high-stakes settings where people may rely on models to interpret records, policies, or complex written material. The engineering value of the project is that it does not stop at showing that LLMs can fail. It offers a concrete way to inspect and evaluate those failures more systematically.

My individual contribution to this project was substantial. I helped define the central research question, develop the claim-level evaluation framing, organize the document-grounded analysis approach, and analyze how unsupported claims appeared in model outputs. I was responsible for moving the project from a general concern about AI accuracy toward a more specific method centered on evidence, traceability, and interpretability. That work now forms the basis of the next stage of the research.

This project matters to me because it sits at the intersection of technical research and real-world accountability. It showed me that the main challenge with AI in high-stakes settings is not only output quality, but whether a system can justify what it says. My research contributes to that problem by showing why unsupported claims are difficult to catch and why claim-level validation offers a stronger path forward. For me, that is the most important result of the project: not simply that LLMs can make mistakes, but that reliable use of these systems requires better methods for checking what those systems claim against what the evidence actually supports.

## Final Personalization Pass

Before exporting the final PDF, improve this draft one more step by adding:

- one sentence with the number of documents, prompts, or models you actually used
- one sentence with your clearest empirical result
- one edit in your own wording so the voice sounds unmistakably like you
