# Emerita/Emeritus Society Undergraduate Research Award Draft

## Recommended Research Title

Evaluating Claim-Level Reliability in Large Language Model Interpretation of Special Education Documents

## Alternate Title

A Claim-Level Validation Framework for Reliable Interpretation of Special Education Documents

## Draft Abstract

Large language models are increasingly used to interpret complex documents, but in high-stakes settings they can produce confident statements that are not adequately supported by source evidence. My research investigates this problem in special education documents such as Individualized Education Programs and Behavior Intervention Plans, where inaccurate interpretation can affect decisions about student support. To study this issue, I analyzed how large language models interpret these documents and developed a claim-level validation approach that breaks model outputs into individual statements, links those statements to source evidence, and classifies them as explicitly supported, inferred, or unsupported. My work shows that while these systems can assist with document interpretation, they also generate unsupported claims that are difficult to detect without structured evaluation. This project contributes to engineering and applied science by advancing methods for AI reliability, evidence traceability, and human-centered oversight in high-stakes document analysis. The work has broader relevance beyond special education because the same validation approach can support more accountable AI use in healthcare, legal, and compliance settings.

## Supplemental Essay Draft

My research addresses a central problem in applied artificial intelligence: large language models can produce fluent and persuasive outputs even when those outputs are not adequately supported by evidence. This is especially concerning in high-stakes document settings, where readers may trust an answer because it sounds coherent and authoritative. I focused on this problem in special education documents, especially Individualized Education Programs and Behavior Intervention Plans, because these records are information-dense, case-specific, and directly connected to decisions about student support. In such settings, an unsupported summary or recommendation is not a minor technical error. It can distort how people understand a student's documented needs, behavior supports, or educational plan.

The goal of my research was to investigate whether large language model outputs could be evaluated more rigorously at the claim level rather than judged as a single response. Instead of asking whether an answer seemed generally good, I studied whether its individual statements were actually justified by the source documents. This led me to focus on three categories of output: claims directly supported by the documents, claims that could be reasonably inferred from the documents, and claims that were unsupported. The core objective of the project was to make the difference between those categories visible and measurable.

To carry out this research, I worked with special education document materials and structured model prompts designed to produce summaries, interpretations, and case-relevant responses. I then analyzed model outputs by decomposing them into individual claims and comparing those claims against the available source evidence. My method combined structured analysis of the output text with a validation process that examined whether each claim could be grounded in the original record. This approach allowed me to move beyond surface impressions of answer quality and instead study reliability as a relationship between a model's statements and the evidence available to support them.

An important part of the project was recognizing that model errors in this setting are not always obvious. A response may appear highly competent while still blending direct evidence, reasonable inference, and unsupported information into a single paragraph. My work therefore emphasized traceability and interpretability. Rather than treating model output as trustworthy by default, I investigated how a claim-level framework could make hidden reliability problems easier to inspect. This required careful attention to document structure, prompt consistency, and the evaluation of how unsupported claims appeared across different responses.

The results of this project showed that large language models can be useful for interpreting complex documents, but they also produce unsupported claims that are difficult to detect without a more structured evaluation process. In particular, I found that models were capable of generating responses that sounded plausible while overstating, blending, or extending information beyond what was directly grounded in the source documents. This result matters because it shows that apparent fluency is not the same as reliability. My research therefore supports the need for evidence-centered validation methods when LLMs are used in high-stakes document analysis.

The significance of this work is both technical and practical. Technically, it contributes to current work on trustworthy AI by shifting evaluation away from general impressions of output quality and toward claim-level evidence assessment. Practically, it suggests a path for making AI-assisted interpretation more auditable in settings where incorrect or unsupported information could create harm. Although I studied this problem in special education, the broader engineering application extends to other document-grounded domains such as healthcare, legal reasoning, and compliance, where users also need to distinguish between what a model can justify and what it merely asserts.

My individual contribution to this work was substantial and central to the project. I was responsible for shaping the research direction, defining the claim-level reliability problem, developing the evaluation framing, organizing the document-grounded testing approach, and analyzing how unsupported claims appeared in model outputs. I also developed the framework concept that now serves as the basis for the current TRACE research direction. If needed, this paragraph should be adjusted to match the exact division of labor used in your SURCA project, but the final version should make your independent role unmistakably clear.

Overall, this project represents a meaningful undergraduate research contribution because it addresses a real and difficult problem in applied AI, develops a concrete methodological response to that problem, and produces findings with clear scholarly and real-world implications. It demonstrates not only that large language models can assist with complex document interpretation, but also that reliable use of those systems requires better methods for evidence-grounded validation. That insight is the foundation of my continuing work in AI reliability research.

## Final Revision Notes

Before submitting, strengthen this essay further by adding:

- any concrete numbers you have from your SURCA work
- the number of documents, prompts, or models examined
- one sentence naming the most important empirical pattern you observed
- a contribution sentence that exactly matches what you personally did

## Strong Result Sentences You Can Use if They Are True

- The study showed that fluent model outputs could still contain unsupported claims even when they appeared highly confident and well structured.
- The project demonstrated that claim-level analysis revealed reliability failures that would be easy to miss in a general review of the response.
- The results suggested that evidence traceability is a more useful reliability target than a single overall quality judgment.
