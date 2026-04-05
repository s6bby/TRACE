interface MetricCardProps {
  label: string;
  value: string | number;
  caption: string;
  tone: "signal" | "success" | "warn" | "danger";
}

export function MetricCard({
  label,
  value,
  caption,
  tone,
}: MetricCardProps) {
  return (
    <article className={`surface-card metric-card ${tone}`}>
      <span className="metric-label">{label}</span>
      <strong className="metric-value">{value}</strong>
      <span className="metric-caption">{caption}</span>
    </article>
  );
}
