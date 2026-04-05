interface SectionHeaderProps {
  kicker: string;
  title: string;
  description: string;
}

export function SectionHeader({
  kicker,
  title,
  description,
}: SectionHeaderProps) {
  return (
    <div className="section-header">
      <p className="section-kicker">{kicker}</p>
      <h2 className="section-title">{title}</h2>
      <p className="section-copy">{description}</p>
    </div>
  );
}
