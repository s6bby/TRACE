export const featureCards = [
  {
    title: "Claim-level validation",
    description:
      "TRACE does not judge a response as one block. It breaks the answer into claims so each statement can be reviewed on its own.",
  },
  {
    title: "Evidence-grounded review",
    description:
      "Each claim is paired with candidate snippets from the uploaded documents so a reviewer can inspect what the system is relying on.",
  },
  {
    title: "High-stakes interpretability",
    description:
      "The initial research focus is special education documents such as IEPs and BIPs, where unsupported interpretation can create real risk.",
  },
] as const;

export const howToUseTrace = [
  "Upload the source documents you want the model response checked against.",
  "Paste the prompt if it helps explain the context, then paste the model response in the main field.",
  "Run TRACE to send the files and response to the backend pipeline for scanning, claim extraction, retrieval, evaluation, and final validation.",
  "Use the process terminal plus claim queue to explain how the backend reached the output and which claims need manual review.",
] as const;

export const supportLabelGuide = [
  "Explicit means the claim is directly grounded in the source material.",
  "Inferred means TRACE found candidate evidence, but the current evaluator has not yet proven direct support.",
  "Unsupported means the claim was not grounded by the evidence returned for this run and should stay in manual review.",
] as const;

export const terminalGuide = [
  "The terminal shows backend document intake, claim extraction, evidence retrieval, evaluation, and validation in sequence.",
  "Detailed claim-level logs are shown for the first several claims so the user can follow the process without reading noise for very large responses.",
  "The current backend runs deterministic retrieval and validation with local-model hooks reserved for the next phase.",
] as const;

export const documentationSections = [
  {
    title: "What TRACE is testing",
    body:
      "TRACE is a claim-level reliability framework for document-grounded LLM outputs. The goal is to determine whether individual statements in a model response are supported by the source evidence, not just whether the overall answer sounds plausible.",
  },
  {
    title: "How to edit the frontend",
    body:
      "The root Vite app owns the UI. Edit src/App.tsx for page composition and flow, src/styles.css for the visual system, src/components for reusable interface blocks, and src/content/siteContent.ts for the user-facing copy.",
  },
  {
    title: "Current runtime",
    body:
      "The root Vite app is now a frontend for the FastAPI backend under backend/src/trace_backend. The browser uploads the source files and response text, and the backend returns the report used to populate the terminal, summary cards, and claim queue.",
  },
  {
    title: "Research context",
    body:
      "The initial evaluation domain is special education document interpretation, especially IEPs and BIPs, but the broader idea is a model-agnostic framework for evidence-grounded review in high-stakes domains.",
  },
] as const;

export const aboutCards = [
  {
    title: "Purpose",
    description:
      "TRACE investigates whether AI outputs can be made more traceable by requiring claim-level justification against uploaded documents.",
  },
  {
    title: "Current scope",
    description:
      "This version runs the backend scanner, claim extractor, hybrid retrieval layer, heuristic evaluator, and deterministic report validation through the web app.",
  },
  {
    title: "Why it matters",
    description:
      "The point is not to prove absolute truth. The point is to make unsupported or weakly justified model statements easier to spot in human review.",
  },
] as const;
