import type { ProcessLogger, ReliabilityReport, ReportSummary } from "./types";

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function summarizeReport(report: ReliabilityReport): ReportSummary {
  if (report.summary) {
    return report.summary;
  }

  return report.assessments.reduce<ReportSummary>(
    (summary, assessment) => {
      summary.totalClaims += 1;

      if (assessment.label === "explicit") {
        summary.explicit += 1;
      } else if (assessment.label === "inferred") {
        summary.inferred += 1;
      } else {
        summary.unsupported += 1;
      }

      if (assessment.claim.ambiguous) {
        summary.ambiguousClaims += 1;
      }

      if (assessment.reviewPriority === "high") {
        summary.highPriority += 1;
      }

      if (assessment.agreementStatus === "contested") {
        summary.contested += 1;
      }

      if (assessment.citedEvidenceIds.length > 0) {
        summary.evidenceBackedClaims += 1;
      }

      summary.retrievalWarnings += assessment.validationFindings.filter((finding) =>
        finding.code.startsWith("retrieval-"),
      ).length;
      summary.validationErrors += assessment.validationFindings.filter(
        (finding) => finding.severity === "error",
      ).length;

      return summary;
    },
    {
      totalClaims: 0,
      explicit: 0,
      inferred: 0,
      unsupported: 0,
      ambiguousClaims: 0,
      highPriority: 0,
      contested: 0,
      evidenceBackedClaims: 0,
      retrievalWarnings: 0,
      validationErrors: 0,
      evidenceCoverage: 0,
      citationValidityRate: 0,
    },
  );
}

export function appendBackendProcessLogs(report: ReliabilityReport, onLog?: ProcessLogger) {
  if (!onLog) {
    return;
  }

  const summary = summarizeReport(report);
  const metadata = report.metadata;
  const sourceDocuments = metadata?.sourceDocuments ?? [];
  const extractionMetrics = metadata?.claimExtractionMetrics;
  const totalWarnings = report.findings.filter((finding) => finding.severity === "warning").length;
  const semanticEnabled = report.assessments.some((assessment) => {
    const retrievalMetadata = assessment.metadata?.retrieval_metadata;
    return Boolean(
      retrievalMetadata &&
        typeof retrievalMetadata === "object" &&
        "semantic_enabled" in retrievalMetadata &&
        retrievalMetadata.semantic_enabled === true,
    );
  });

  if (sourceDocuments.length > 0) {
    onLog({
      stage: "ingest",
      tone: "success",
      message: `Backend scanned ${sourceDocuments.length} source document(s) into the evidence pool.`,
    });

    const docLimit = 4;
    sourceDocuments.slice(0, docLimit).forEach((document) => {
      const details = [
        document.fileKind.toUpperCase(),
        `${document.pageCount} page(s)`,
        document.findingCount > 0 ? `${document.findingCount} scan finding(s)` : "no scan findings",
      ].join(" | ");

      onLog({
        stage: "ingest",
        message: `Indexed ${document.documentId}: ${details}.`,
        tone: document.findingCount > 0 ? "warn" : "info",
      });
    });

    if (sourceDocuments.length > docLimit) {
      onLog({
        stage: "ingest",
        message: `${sourceDocuments.length - docLimit} additional document(s) were indexed without listing every file here.`,
      });
    }
  }

  if (extractionMetrics) {
    onLog({
      stage: "claims",
      tone: extractionMetrics.ambiguousClaimCount > 0 ? "warn" : "success",
      message: `Claim extraction produced ${extractionMetrics.claimCount} claim(s) from ${extractionMetrics.sentenceCount} sentence(s); ${extractionMetrics.ambiguousClaimCount} claim(s) were flagged as ambiguous.`,
    });
  }

  const ambiguousClaims = report.assessments.filter((assessment) => assessment.claim.ambiguous);
  ambiguousClaims.slice(0, 3).forEach((assessment) => {
    onLog({
      stage: "claims",
      tone: "warn",
      message: `${assessment.claim.claimId} requires extra review because the claim boundary was marked ambiguous.`,
    });
  });

  const retrievalCandidateCount = report.assessments.reduce((count, assessment) => {
    return count + assessment.evidence.length;
  }, 0);
  onLog({
    stage: "retrieval",
    tone: summary.retrievalWarnings > 0 ? "warn" : "success",
    message: `Evidence retrieval ran in ${semanticEnabled ? "hybrid" : "lexical-only"} mode and returned ${retrievalCandidateCount} cited evidence span(s) across the final report.`,
  });

  report.assessments.slice(0, 6).forEach((assessment, index) => {
    const citedCount = assessment.citedEvidenceIds.length;
    onLog({
      stage: "evaluation",
      tone:
        assessment.label === "unsupported" || assessment.reviewPriority === "high"
          ? "warn"
          : "info",
      message: `Claim ${index + 1} resolved as ${assessment.label}; ${citedCount} citation(s), ${assessment.agreementStatus.replace("_", " ")} review mode, ${assessment.reviewPriority} priority.`,
    });
  });

  if (report.assessments.length > 6) {
    onLog({
      stage: "evaluation",
      message: `${report.assessments.length - 6} additional claim evaluations were completed and included in the report.`,
    });
  }

  onLog({
    stage: "validation",
    tone:
      summary.validationErrors > 0 ? "error" : totalWarnings > 0 ? "warn" : "success",
    message: `Validation finished with ${summary.validationErrors} error(s) and ${totalWarnings} warning(s). Citation validity is ${formatPercent(summary.citationValidityRate)}.`,
  });

  onLog({
    stage: "report",
    tone: "success",
    message: `Report assembled with ${summary.totalClaims} claim(s), ${summary.highPriority} high-priority review item(s), and ${formatPercent(summary.evidenceCoverage)} evidence coverage.`,
  });
}

export function truncateText(text: string, limit = 200) {
  const compact = text.replace(/\s+/g, " ").trim();
  if (compact.length <= limit) {
    return compact;
  }

  return `${compact.slice(0, limit - 3).trimEnd()}...`;
}
