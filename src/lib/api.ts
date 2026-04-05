import type {
  Claim,
  ClaimAssessment,
  ClaimExtractionMetrics,
  EvidenceSpan,
  JudgeDecision,
  ProcessLogger,
  ReliabilityReport,
  ReportMetadata,
  ReportSummary,
  SourceDocumentSummary,
  ValidationFinding,
} from "./types";

const API_BASE_URL = (import.meta.env.VITE_TRACE_API_BASE_URL ?? "").replace(/\/$/, "");

function apiUrl(path: string) {
  return API_BASE_URL ? `${API_BASE_URL}${path}` : path;
}

function asRecord(value: unknown): Record<string, unknown> {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return {};
}

function asArray<T>(value: unknown, mapper: (item: unknown) => T): T[] {
  return Array.isArray(value) ? value.map(mapper) : [];
}

function asString(value: unknown, fallback = "") {
  return typeof value === "string" ? value : fallback;
}

function asNumber(value: unknown, fallback = 0) {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function asNullableNumber(value: unknown) {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function asBoolean(value: unknown, fallback = false) {
  return typeof value === "boolean" ? value : fallback;
}

function normalizeFinding(input: unknown): ValidationFinding {
  const record = asRecord(input);
  return {
    code: asString(record.code),
    severity:
      record.severity === "error" || record.severity === "warning" || record.severity === "info"
        ? record.severity
        : "info",
    message: asString(record.message),
    claimId: asString(record.claim_id || record.claimId) || undefined,
    evidenceId: asString(record.evidence_id || record.evidenceId) || undefined,
    documentId: asString(record.document_id || record.documentId) || undefined,
    metadata: asRecord(record.metadata),
  };
}

function normalizeClaim(input: unknown): Claim {
  const record = asRecord(input);
  return {
    claimId: asString(record.claim_id || record.claimId),
    text: asString(record.text),
    responseSpan: asString(record.response_span || record.responseSpan) || undefined,
    claimType: asString(record.claim_type || record.claimType) || undefined,
    ambiguous: asBoolean(record.ambiguous),
    ambiguityReasons: asArray(record.ambiguity_reasons || record.ambiguityReasons, (item) =>
      asString(item),
    ),
    metadata: asRecord(record.metadata),
  };
}

function normalizeEvidence(input: unknown): EvidenceSpan {
  const record = asRecord(input);
  return {
    evidenceId: asString(record.evidence_id || record.evidenceId) || undefined,
    documentId: asString(record.document_id || record.documentId),
    sourcePath: asString(record.source_path || record.sourcePath) || undefined,
    snippet: asString(record.snippet),
    section: asString(record.section) || null,
    pageNumber: asNullableNumber(record.page_number || record.pageNumber),
    blockKind: asString(record.block_kind || record.blockKind) || undefined,
    retrievalRank: asNumber(record.retrieval_rank || record.retrievalRank, 0) || undefined,
    score: asNullableNumber(record.fused_score || record.score),
    lexicalScore: asNullableNumber(record.lexical_score || record.lexicalScore),
    semanticScore: asNullableNumber(record.semantic_score || record.semanticScore),
    metadata: asRecord(record.metadata),
  };
}

function normalizeJudgeDecision(input: unknown): JudgeDecision {
  const record = asRecord(input);
  return {
    judgeId: asString(record.judge_id || record.judgeId),
    label:
      record.label === "explicit" || record.label === "unsupported" || record.label === "inferred"
        ? record.label
        : "unsupported",
    citedEvidenceIds: asArray(record.cited_evidence_ids || record.citedEvidenceIds, (item) =>
      asString(item),
    ),
    rationale: asString(record.rationale),
    ambiguityNote: asString(record.ambiguity_note || record.ambiguityNote) || undefined,
    reviewPriority:
      record.review_priority === "low" ||
      record.review_priority === "high" ||
      record.reviewPriority === "low" ||
      record.reviewPriority === "high"
        ? ((record.review_priority || record.reviewPriority) as "low" | "high")
        : "normal",
    metadata: asRecord(record.metadata),
  };
}

function normalizeAssessment(input: unknown): ClaimAssessment {
  const record = asRecord(input);
  return {
    claim: normalizeClaim(record.claim),
    label:
      record.label === "explicit" || record.label === "unsupported" || record.label === "inferred"
        ? record.label
        : "unsupported",
    evidence: asArray(record.evidence, normalizeEvidence),
    citedEvidenceIds: asArray(record.cited_evidence_ids || record.citedEvidenceIds, (item) =>
      asString(item),
    ),
    note: asString(record.note),
    reviewPriority:
      record.review_priority === "low" ||
      record.review_priority === "high" ||
      record.reviewPriority === "low" ||
      record.reviewPriority === "high"
        ? ((record.review_priority || record.reviewPriority) as "low" | "high")
        : "normal",
    agreementStatus:
      record.agreement_status === "single_judge" ||
      record.agreement_status === "consensus" ||
      record.agreement_status === "adjudicated" ||
      record.agreement_status === "contested" ||
      record.agreementStatus === "single_judge" ||
      record.agreementStatus === "consensus" ||
      record.agreementStatus === "adjudicated" ||
      record.agreementStatus === "contested"
        ? ((record.agreement_status || record.agreementStatus) as ClaimAssessment["agreementStatus"])
        : "heuristic",
    judgeDecisions: asArray(record.judge_decisions || record.judgeDecisions, normalizeJudgeDecision),
    validationFindings: asArray(
      record.validation_findings || record.validationFindings,
      normalizeFinding,
    ),
    metadata: asRecord(record.metadata),
  };
}

function normalizeSummary(input: unknown): ReportSummary | undefined {
  const record = asRecord(input);
  if (!Object.keys(record).length) {
    return undefined;
  }
  return {
    totalClaims: asNumber(record.total_claims || record.totalClaims),
    explicit: asNumber(record.explicit_count || record.explicit),
    inferred: asNumber(record.inferred_count || record.inferred),
    unsupported: asNumber(record.unsupported_count || record.unsupported),
    ambiguousClaims: asNumber(record.ambiguous_claim_count || record.ambiguousClaims),
    highPriority: asNumber(record.high_priority_count || record.highPriority),
    contested: asNumber(record.contested_count || record.contested),
    evidenceBackedClaims: asNumber(
      record.evidence_backed_claim_count || record.evidenceBackedClaims,
    ),
    retrievalWarnings: asNumber(record.retrieval_warning_count || record.retrievalWarnings),
    validationErrors: asNumber(record.validation_error_count || record.validationErrors),
    evidenceCoverage: asNumber(record.evidence_coverage || record.evidenceCoverage),
    citationValidityRate: asNumber(
      record.citation_validity_rate || record.citationValidityRate,
    ),
  };
}

function normalizeSourceDocumentSummary(input: unknown): SourceDocumentSummary {
  const record = asRecord(input);
  return {
    documentId: asString(record.document_id || record.documentId),
    sourcePath: asString(record.source_path || record.sourcePath),
    fileKind: asString(record.file_kind || record.fileKind),
    pageCount: asNumber(record.page_count || record.pageCount),
    findingCount: asNumber(record.finding_count || record.findingCount),
  };
}

function normalizeClaimExtractionMetrics(input: unknown): ClaimExtractionMetrics | undefined {
  const record = asRecord(input);
  if (!Object.keys(record).length) {
    return undefined;
  }
  return {
    blockCount: asNumber(record.block_count || record.blockCount),
    sentenceCount: asNumber(record.sentence_count || record.sentenceCount),
    claimCount: asNumber(record.claim_count || record.claimCount),
    ambiguousClaimCount: asNumber(
      record.ambiguous_claim_count || record.ambiguousClaimCount,
    ),
    skippedHeadingCount: asNumber(
      record.skipped_heading_count || record.skippedHeadingCount,
    ),
    skippedQuestionCount: asNumber(
      record.skipped_question_count || record.skippedQuestionCount,
    ),
    skippedFragmentCount: asNumber(
      record.skipped_fragment_count || record.skippedFragmentCount,
    ),
  };
}

function normalizeMetadata(input: unknown): ReportMetadata | undefined {
  const record = asRecord(input);
  if (!Object.keys(record).length) {
    return undefined;
  }

  return {
    ...record,
    generatedAt: asString(record.generated_at || record.generatedAt) || undefined,
    claimExtractionMetrics: normalizeClaimExtractionMetrics(
      record.claim_extraction_metrics || record.claimExtractionMetrics,
    ),
    claimExtractionFindings: asArray(
      record.claim_extraction_findings || record.claimExtractionFindings,
      normalizeFinding,
    ),
    documentCount: asNumber(record.document_count || record.documentCount, 0) || undefined,
    sourceDocuments: asArray(
      record.source_documents || record.sourceDocuments,
      normalizeSourceDocumentSummary,
    ),
  };
}

export function normalizeReport(payload: unknown): ReliabilityReport {
  const record = asRecord(payload);
  return {
    caseId: asString(record.case_id || record.caseId),
    assessments: asArray(record.assessments, normalizeAssessment),
    summary: normalizeSummary(record.summary),
    findings: asArray(record.findings, normalizeFinding),
    metadata: normalizeMetadata(record.metadata),
  };
}

async function parseError(response: Response) {
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
    if (payload.detail != null) {
      return JSON.stringify(payload.detail);
    }
  }

  const text = await response.text();
  return text || `TRACE backend request failed with status ${response.status}.`;
}

async function ensureBackendAvailable(onLog?: ProcessLogger) {
  onLog?.({
    stage: "session",
    message: "Checking TRACE backend availability.",
  });

  const response = await fetch(apiUrl("/health"));
  if (!response.ok) {
    throw new Error(`TRACE backend health check failed with status ${response.status}.`);
  }
}

export async function analyzeWithBackend(
  caseId: string,
  responseText: string,
  files: File[],
  onLog?: ProcessLogger,
): Promise<ReliabilityReport> {
  await ensureBackendAvailable(onLog);

  onLog?.({
    stage: "session",
    message: `Uploading ${files.length} document(s) to the TRACE backend.`,
  });

  const formData = new FormData();
  formData.set("case_id", caseId);
  formData.set("response_text", responseText);

  files.forEach((file) => {
    formData.append("documents", file, file.name);
  });

  const response = await fetch(apiUrl("/api/v1/analyze"), {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  onLog?.({
    stage: "session",
    tone: "success",
    message: "TRACE backend completed the analysis request and returned a structured report.",
  });

  return normalizeReport(await response.json());
}
