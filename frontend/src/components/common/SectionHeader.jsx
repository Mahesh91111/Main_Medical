
export default function SectionHeader({
  title,
  description,
  action
}) {
  return (
    <div className="section-header">
      <div>
        <h3>{title}</h3>
        {description && <p>{description}</p>}
      </div>

      {action && (
        <div className="section-header-action">
          {action}
        </div>
      )}
    </div>
  );
}
