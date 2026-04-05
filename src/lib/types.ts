export type SupportLabel = "explicit" | "inferred" | "unsupported";
export type ReviewPriority = "low" | "normal" | "high";
export type AgreementStatus =
  | "heuristic"
  | "single_judge"
  | "consensus"
  | "adjudicated"
  | "contested";
export type FindingSeverity = "info" | "warning" | "error";

export interface SourceDocument {
  documentId: string;
  title: string;
  text: string;
  section?: string | null;
}

export interface Claim {
  claimId: string;
  text: string;
  responseSpan?: string | null;
  claimType?: string;
  ambiguous: boolean;
  ambiguityReasons?: string[];
  metadata?: Record<string, unknown>;
}

export interface EvidenceSpan {
  evidenceId?: string;
  documentId: string;
  sourcePath?: string;
  snippet: string;
  section?: string | null;
  pageNumber?: number | null;
  blockKind?: string;
  retrievalRank?: number;
  score?: number | null;
  lexicalScore?: number | null;
  semanticScore?: number | null;
  metadata?: Record<string, unknown>;
}

export interface ValidationFinding {
  code: string;
  severity: FindingSeverity;
  message: string;
  claimId?: string;
  evidenceId?: string;
  documentId?: string;
  metadata?: Record<string, unknown>;
}

export interface JudgeDecision {
  judgeId: string;
  label: SupportLabel;
  citedEvidenceIds: string[];
  rationale: string;
  ambiguityNote?: string;
  reviewPriority: ReviewPriority;
  metadata?: Record<string, unknown>;
}

export interface ClaimAssessment {
  claim: Claim;
  label: SupportLabel;
  evidence: EvidenceSpan[];
  citedEvidenceIds: string[];
  note: string;
  reviewPriority: ReviewPriority;
  agreementStatus: AgreementStatus;
  judgeDecisions: JudgeDecision[];
  validationFindings: ValidationFinding[];
  metadata?: Record<string, unknown>;
}

export interface ReportSummary {
  totalClaims: number;
  explicit: number;
  inferred: number;
  unsupported: number;
  ambiguousClaims: number;
  highPriority: number;
  contested: number;
  evidenceBackedClaims: number;
  retrievalWarnings: number;
  validationErrors: number;
  evidenceCoverage: number;
  citationValidityRate: number;
}

export interface SourceDocumentSummary {
  documentId: string;
  sourcePath: string;
  fileKind: string;
  pageCount: number;
  findingCount: number;
}

export interface ClaimExtractionMetrics {
  blockCount: number;
  sentenceCount: number;
  claimCount: number;
  ambiguousClaimCount: number;
  skippedHeadingCount: number;
  skippedQuestionCount: number;
  skippedFragmentCount: number;
}

export interface ReportMetadata {
  generatedAt?: string;
  claimExtractionMetrics?: ClaimExtractionMetrics;
  claimExtractionFindings?: ValidationFinding[];
  documentCount?: number;
  sourceDocuments?: SourceDocumentSummary[];
  [key: string]: unknown;
}

export interface ReliabilityReport {
  caseId: string;
  assessments: ClaimAssessment[];
  summary?: ReportSummary;
  findings: ValidationFinding[];
  metadata?: ReportMetadata;
}

export interface AnalysisSnapshot {
  report: ReliabilityReport;
  documentCount: number;
  documentNames: string[];
  prompt: string;
  response: string;
  timestamp: string;
}

export type ProcessLogTone = "info" | "success" | "warn" | "error";

export interface ProcessLogEntry {
  id: string;
  timestamp: string;
  stage: string;
  message: string;
  tone: ProcessLogTone;
}

export interface ProcessLogInput {
  stage: string;
  message: string;
  tone?: ProcessLogTone;
}

export type ProcessLogger = (entry: ProcessLogInput) => void;
