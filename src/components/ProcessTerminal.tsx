import type { ProcessLogEntry } from "../lib/types";

interface ProcessTerminalProps {
  entries: ProcessLogEntry[];
  state: "idle" | "running" | "complete" | "error";
}

export function ProcessTerminal({
  entries,
  state,
}: ProcessTerminalProps) {
  return (
    <section className="surface-card terminal-shell">
      <div className="terminal-topline">
        <div>
          <p className="terminal-kicker">Process Terminal</p>
          <h3>How TRACE is analyzing the material</h3>
        </div>
        <span className={`run-state ${state}`}>{state}</span>
      </div>

      <p className="terminal-intro">
        TRACE logs document intake, claim extraction, evidence retrieval, and
        report assembly here so the operator can explain what happened without
        reading backend internals.
      </p>

      <div className="terminal-window" role="log" aria-live="polite">
        {entries.length > 0 ? (
          entries.map((entry) => (
            <div className={`terminal-line ${entry.tone}`} key={entry.id}>
              <span className="terminal-time">{entry.timestamp}</span>
              <span className="terminal-stage">{entry.stage}</span>
              <span className="terminal-message">{entry.message}</span>
            </div>
          ))
        ) : (
          <div className="terminal-line idle">
            <span className="terminal-time">--:--:--</span>
            <span className="terminal-stage">ready</span>
            <span className="terminal-message">
              Upload source documents, paste a model response, and run TRACE to
              watch the pipeline steps appear here.
            </span>
          </div>
        )}
      </div>
    </section>
  );
}
