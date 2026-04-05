interface InfoCardProps {
  title: string;
  intro: string;
  items: readonly string[];
}

export function InfoCard({ title, intro, items }: InfoCardProps) {
  return (
    <article className="surface-card info-card">
      <h3>{title}</h3>
      <p>{intro}</p>
      <div className="signal-list">
        {items.map((item) => (
          <div className="signal-item" key={item}>
            <span className="signal-dot" />
            <span>{item}</span>
          </div>
        ))}
      </div>
    </article>
  );
}
