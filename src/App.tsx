import { startTransition, useState } from "react";

import { AssessmentCard } from "./components/AssessmentCard";
import { FeatureCard } from "./components/FeatureCard";
import { InfoCard } from "./components/InfoCard";
import { MetricCard } from "./components/MetricCard";
import { ProcessTerminal } from "./components/ProcessTerminal";
import { SectionHeader } from "./components/SectionHeader";
import {
  aboutCards,
  documentationSections,
  featureCards,
  howToUseTrace,
  supportLabelGuide,
  terminalGuide,
} from "./content/siteContent";
import { analyzeWithBackend } from "./lib/api";
import { appendBackendProcessLogs, summarizeReport, truncateText } from "./lib/trace";
import type { AnalysisSnapshot, ProcessLogEntry, ProcessLogInput } from "./lib/types";

type TabId = "demo" | "documentation" | "about";
type RunState = "idle" | "running" | "complete" | "error";

function formatTimestamp(date: Date) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>("demo");
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [userPrompt, setUserPrompt] = useState("");
  const [responseText, setResponseText] = useState("");
  const [snapshot, setSnapshot] = useState<AnalysisSnapshot | null>(null);
  const [runState, setRunState] = useState<RunState>("idle");
  const [statusMessages, setStatusMessages] = useState<ProcessLogEntry[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  function appendStatus(entry: ProcessLogInput) {
    const timestamp = new Intl.DateTimeFormat("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    }).format(new Date());

    const logEntry: ProcessLogEntry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      timestamp,
      stage: entry.stage,
      message: entry.message,
      tone: entry.tone ?? "info",
    };

    setStatusMessages((current) => [...current, logEntry]);
  }

  async function handleAnalyze() {
    setErrorMessage(null);
    setStatusMessages([]);

    if (uploadedFiles.length === 0) {
      setRunState("error");
      appendStatus({
        stage: "validation",
        tone: "error",
        message: "TRACE could not start because no source documents were uploaded.",
      });
      setErrorMessage("Upload at least one source document before running TRACE.");
      return;
    }

    if (!responseText.trim()) {
      setRunState("error");
      appendStatus({
        stage: "validation",
        tone: "error",
        message: "TRACE could not start because the model response field was empty.",
      });
      setErrorMessage("Paste a model response so TRACE has claims to review.");
      return;
    }

    setRunState("running");
    appendStatus({
      stage: "session",
      message: "TRACE session initialized. Waiting for the backend analysis pipeline to finish.",
    });

    try {
      const report = await analyzeWithBackend("analysis", responseText, uploadedFiles, appendStatus);
      appendBackendProcessLogs(report, appendStatus);

      appendStatus({
        stage: "session",
        tone: "success",
        message: "TRACE finished processing. The report and claim queue are now ready for review.",
      });
      startTransition(() => {
        setSnapshot({
          report,
          documentCount: uploadedFiles.length,
          documentNames: uploadedFiles.map((document) => document.name),
          prompt: userPrompt.trim(),
          response: responseText.trim(),
          timestamp: formatTimestamp(new Date()),
        });
        setRunState("complete");
      });
    } catch (error) {
      setRunState("error");
      appendStatus({
        stage: "error",
        tone: "error",
        message:
          error instanceof Error
            ? error.message
            : "TRACE could not complete the analysis.",
      });
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "TRACE could not complete the analysis.",
      );
    }
  }

  const summary = snapshot ? summarizeReport(snapshot.report) : null;

  return (
    <div className="app-shell">
      <header className="hero-panel">
        <span className="hero-kicker">TRACE Reliability Studio</span>
        <h1 className="hero-title">Claim-level reliability checks for document-grounded AI outputs.</h1>
        <p className="hero-copy">
          TRACE is a research prototype for testing whether a model response is
          actually justified by the documents behind it. It breaks the response
          into claims, scans the uploaded evidence corpus, retrieves candidate
          support, and labels each claim as explicit, inferred, or unsupported
          to support human review.
        </p>
        <div className="hero-grid">
          <div className="hero-stat">
            <span className="hero-stat-label">Core Task</span>
            <span className="hero-stat-value">
              Decompose a model answer into claims and review each statement
              against uploaded source material.
            </span>
          </div>
          <div className="hero-stat">
            <span className="hero-stat-label">Support Labels</span>
            <span className="hero-stat-value">
              TRACE distinguishes between explicit support, inferred support,
              and unsupported claims.
            </span>
          </div>
          <div className="hero-stat">
            <span className="hero-stat-label">Research Domain</span>
            <span className="hero-stat-value">
              The initial testbed is high-stakes special education document
              interpretation, especially IEPs and BIPs.
            </span>
          </div>
        </div>
      </header>

      <section className="feature-grid">
        {featureCards.map((card) => (
          <FeatureCard
            key={card.title}
            title={card.title}
            description={card.description}
          />
        ))}
      </section>

      <nav className="tab-nav" aria-label="Primary">
        {(["demo", "documentation", "about"] as const).map((tab) => (
          <button
            type="button"
            key={tab}
            className={tab === activeTab ? "tab-button active" : "tab-button"}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>

      {activeTab === "demo" ? (
        <main className="page-panel">
          <SectionHeader
            kicker="Workspace"
            title="Upload source evidence and inspect how TRACE reasons through the response"
            description="Start with the documents the model should be grounded in, then paste the response you want checked. The Vite app now sends the run to the backend scanner, extractor, retriever, and validator so you can inspect the real pipeline output."
          />

          <section className="workspace-grid">
            <div className="workspace-main surface-card">
              <div className="field-block">
                <label htmlFor="source-documents">Source documents</label>
                <input
                  id="source-documents"
                  className="file-input"
                  type="file"
                  multiple
                  accept=".txt,.pdf,.docx,text/plain,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  onChange={(event) => {
                    const nextFiles = Array.from(event.target.files ?? []);
                    setUploadedFiles(nextFiles);
                  }}
                />
                <p className="field-help">
                  Upload the documents that should ground the model response.
                  TRACE sends PDF, DOCX, and TXT files to the backend scanner,
                  which extracts text and builds the evidence pool for the run.
                </p>
                {uploadedFiles.length > 0 ? (
                  <div className="pill-row">
                    {uploadedFiles.map((file) => (
                      <span className="pill" key={file.name}>
                        {file.name}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>

              <div className="field-block">
                <label htmlFor="prompt-context">Prompt context</label>
                <textarea
                  id="prompt-context"
                  rows={4}
                  placeholder="Optional: paste the original prompt or task instructions to preserve context for the reviewer."
                  value={userPrompt}
                  onChange={(event) => setUserPrompt(event.target.value)}
                />
                <p className="field-help">
                  This field is not scored directly, but it helps explain what
                  the model was trying to do.
                </p>
              </div>

              <div className="field-block">
                <label htmlFor="model-response">Model response</label>
                <textarea
                  id="model-response"
                  rows={10}
                  placeholder="Paste the model response here. The backend will decompose it into claims, retrieve evidence, and build a validation report."
                  value={responseText}
                  onChange={(event) => setResponseText(event.target.value)}
                />
                <p className="field-help">
                  Full paragraphs are supported. TRACE will extract claims from
                  the response text before retrieval and validation.
                </p>
              </div>

              <button
                type="button"
                className="primary-button"
                onClick={() => void handleAnalyze()}
                disabled={runState === "running"}
              >
                {runState === "running" ? "Running TRACE analysis..." : "Run TRACE analysis"}
              </button>

              {errorMessage ? <p className="error-banner">{errorMessage}</p> : null}
            </div>

            <div className="workspace-side">
              <InfoCard
                title="How to use TRACE"
                intro="This interface is designed to make the review workflow legible to both the operator and the audience."
                items={howToUseTrace}
              />
              <InfoCard
                title="Support label guide"
                intro="These labels help distinguish directly supported claims from weaker or missing grounding."
                items={supportLabelGuide}
              />
              <InfoCard
                title="What the terminal shows"
                intro="The process terminal is there to reveal the pipeline, not just the final answer."
                items={terminalGuide}
              />
            </div>
          </section>

          <ProcessTerminal entries={statusMessages} state={runState} />

          {snapshot && summary ? (
            <section className="report-stack">
              <SectionHeader
                kicker="Live Output"
                title="Reliability summary and claim queue"
                description="TRACE highlights the output structure first, then lets the reviewer inspect each claim, its support label, and the candidate evidence behind it."
              />

              <div className="metrics-grid">
                <MetricCard
                  label="Claims Reviewed"
                  value={summary.totalClaims}
                  caption="Distinct claims extracted from the model response."
                  tone="signal"
                />
                <MetricCard
                  label="Explicit Support"
                  value={summary.explicit}
                  caption="Claims directly grounded in source material."
                  tone="success"
                />
                <MetricCard
                  label="Inferred Support"
                  value={summary.inferred}
                  caption="Claims with candidate evidence but no strict proof label yet."
                  tone="warn"
                />
                <MetricCard
                  label="Manual Review"
                  value={summary.unsupported}
                  caption="Claims that still need stronger evidence retrieval."
                  tone="danger"
                />
              </div>

              <div className="report-grid">
                <article className="surface-card info-card">
                  <h3>Executive summary</h3>
                  <p>
                    TRACE is designed to make model behavior easier to audit.
                    The goal is not to collapse everything into one score. The
                    goal is to show which claims look grounded, which claims are
                    only weakly supported, and where a human reviewer should focus.
                  </p>
                  <div className="signal-list">
                    <div className="signal-item">
                      <span className="signal-dot" />
                      <span>{snapshot.documentCount} source document(s) supplied to the evidence pool.</span>
                    </div>
                    <div className="signal-item">
                      <span className="signal-dot" />
                      <span>{summary.highPriority} claim(s) marked high priority for manual review.</span>
                    </div>
                    <div className="signal-item">
                      <span className="signal-dot" />
                      <span>Citation validity: {Math.round(summary.citationValidityRate * 100)}%.</span>
                    </div>
                    <div className="signal-item">
                      <span className="signal-dot" />
                      <span>Last analysis run: {snapshot.timestamp}.</span>
                    </div>
                  </div>
                  {snapshot.prompt ? (
                    <div className="summary-block">
                      <h4>Prompt context</h4>
                      <p>{truncateText(snapshot.prompt, 320)}</p>
                    </div>
                  ) : null}
                </article>

                <article className="surface-card info-card">
                  <h3>Run details</h3>
                  <p>
                    This run reflects the backend pipeline rather than the old
                    in-browser prototype. The report below comes from the
                    scanner, claim extractor, retriever, evaluator, and final
                    validation layer running through the FastAPI service.
                  </p>
                  <div className="signal-list">
                    <div className="signal-item">
                      <span className="signal-dot" />
                      <span>{summary.ambiguousClaims} ambiguous claim(s) flagged during extraction.</span>
                    </div>
                    <div className="signal-item">
                      <span className="signal-dot" />
                      <span>{summary.retrievalWarnings} retrieval warning(s) carried into the final report.</span>
                    </div>
                    <div className="signal-item">
                      <span className="signal-dot" />
                      <span>Evidence coverage: {Math.round(summary.evidenceCoverage * 100)}% of claims.</span>
                    </div>
                  </div>
                  <div className="pill-row">
                    {snapshot.documentNames.map((name) => (
                      <span className="pill" key={name}>
                        {name}
                      </span>
                    ))}
                  </div>
                  {snapshot.report.findings.length > 0 ? (
                    <div className="summary-block">
                      <h4>Backend findings</h4>
                      <div className="finding-list">
                        {snapshot.report.findings.slice(0, 4).map((finding, index) => (
                          <div className={`finding-item ${finding.severity}`} key={`${finding.code}-${index}`}>
                            <strong>{finding.severity}</strong>
                            <span>{finding.message}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </article>
              </div>

              <div className="assessment-stack">
                {snapshot.report.assessments.length > 0 ? (
                  snapshot.report.assessments.map((assessment, index) => (
                    <AssessmentCard
                      key={`${assessment.claim.claimId}-${index}`}
                      assessment={assessment}
                      index={index + 1}
                    />
                  ))
                ) : (
                  <div className="empty-state">
                    <h3>No claims were extracted</h3>
                    <p>
                      Add a fuller model response so TRACE has material to decompose
                      into claims and validate.
                    </p>
                  </div>
                )}
              </div>
            </section>
          ) : null}
        </main>
      ) : null}

      {activeTab === "documentation" ? (
        <main className="page-panel">
          <SectionHeader
            kicker="Documentation"
            title="What TRACE is doing and where to edit it"
            description="TRACE is both a research idea and a product surface. These notes explain the reliability workflow, the current backend architecture, and where the frontend now lives."
          />
          <section className="content-grid">
            {documentationSections.map((section) => (
              <article className="surface-card doc-card" key={section.title}>
                <h3>{section.title}</h3>
                <p>{section.body}</p>
              </article>
            ))}
          </section>
        </main>
      ) : null}

      {activeTab === "about" ? (
        <main className="page-panel">
          <SectionHeader
            kicker="About TRACE"
            title="A claim-level reliability framework for document-grounded AI outputs"
            description="TRACE explores whether model responses can be made more traceable and interpretable by requiring evidence-linked claim review instead of relying on a single overall judgment."
          />
          <section className="content-grid">
            {aboutCards.map((card) => (
              <article className="surface-card about-card" key={card.title}>
                <h3>{card.title}</h3>
                <p>{card.description}</p>
              </article>
            ))}
          </section>
        </main>
      ) : null}
    </div>
  );
}
