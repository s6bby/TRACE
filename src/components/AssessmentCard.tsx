import { truncateText } from "../lib/trace";
import type { ClaimAssessment } from "../lib/types";

interface AssessmentCardProps {
  assessment: ClaimAssessment;
  index: number;
}

export function AssessmentCard({
  assessment,
  index,
}: AssessmentCardProps) {
  const labelText = assessment.label.replace("_", " ");
  const priorityText = assessment.reviewPriority;
  const agreementText = assessment.agreementStatus.replace("_", " ");

  return (
    <details
      className="surface-card assessment-card"
      open={index === 1 || assessment.reviewPriority === "high"}
    >
      <summary>
        <span className="assessment-index">Claim {index}</span>
        <span className={`status-pill status-${assessment.label}`}>
          {labelText}
        </span>
        <span className={`priority-pill priority-${priorityText}`}>
          {priorityText} priority
        </span>
        <span className="priority-pill priority-normal">
          {agreementText}
        </span>
      </summary>
      <div className="assessment-body">
        <p className="assessment-claim">{assessment.claim.text}</p>
        <p className="assessment-note">{assessment.note}</p>

        <div className="meta-row">
          {assessment.claim.claimType ? (
            <span className="pill">Type: {assessment.claim.claimType}</span>
          ) : null}
          {assessment.claim.ambiguous ? (
            <span className="pill">Ambiguous boundary</span>
          ) : null}
          {assessment.citedEvidenceIds.length > 0 ? (
            <span className="pill">{assessment.citedEvidenceIds.length} cited evidence id(s)</span>
          ) : null}
        </div>

        {assessment.evidence.length > 0 ? (
          <div className="evidence-list">
            {assessment.evidence.slice(0, 3).map((evidence) => (
              <article
                className="evidence-card"
                key={`${index}-${evidence.evidenceId ?? evidence.documentId}`}
              >
                <span className="evidence-label">
                  Source: {evidence.documentId}
                  {evidence.pageNumber ? ` | page ${evidence.pageNumber}` : ""}
                  {evidence.section ? ` | ${evidence.section}` : ""}
                  {evidence.blockKind ? ` | ${evidence.blockKind}` : ""}
                </span>
                <p>{truncateText(evidence.snippet, 280) || "No snippet available."}</p>
                <div className="meta-row">
                  {evidence.evidenceId ? <span className="pill">ID: {evidence.evidenceId}</span> : null}
                  {typeof evidence.score === "number" ? (
                    <span className="pill">Score: {evidence.score.toFixed(4)}</span>
                  ) : null}
                  {assessment.citedEvidenceIds.includes(evidence.evidenceId ?? "") ? (
                    <span className="pill">Cited in final label</span>
                  ) : null}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state compact">
            <h4>No supporting evidence returned</h4>
            <p>
              This claim remained ungrounded after backend retrieval and should
              stay in the manual review queue.
            </p>
          </div>
        )}

        {assessment.validationFindings.length > 0 ? (
          <div className="summary-block">
            <h4>Validation findings</h4>
            <div className="finding-list">
              {assessment.validationFindings.slice(0, 3).map((finding, findingIndex) => (
                <div className={`finding-item ${finding.severity}`} key={`${finding.code}-${findingIndex}`}>
                  <strong>{finding.severity}</strong>
                  <span>{finding.message}</span>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </details>
  );
}
