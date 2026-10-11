
export default function StatCard({
  title,
  value,
  description,
  icon: Icon,
  tone = "blue"
}) {
  return (
    <article className="stat-card">
      <div className="stat-card-top">
        <span className="stat-title">{title}</span>

        <div className={`stat-icon stat-icon-${tone}`}>
          <Icon size={21} strokeWidth={1.8} />
        </div>
      </div>

      <div className="stat-value">{value}</div>
      <p className="stat-description">{description}</p>
    </article>
  );
}
