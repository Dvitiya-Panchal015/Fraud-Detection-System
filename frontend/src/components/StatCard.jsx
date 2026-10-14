import React from "react";

export default function StatCard({
  label,
  value,
  detail,
  icon: Icon,
  tone = "cyan",
}) {
  return (
    <article className="stat-card panel">
      <div className={`stat-icon tone-${tone}`}>
        <Icon size={19} strokeWidth={1.8} />
      </div>
      <p className="stat-label">{label}</p>
      <p className="stat-value">{value}</p>
      <p className="stat-detail">{detail}</p>
    </article>
  );
}