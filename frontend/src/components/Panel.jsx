import React from "react";

export default function Panel({
  title,
  subtitle,
  action,
  children,
  className = "",
}) {
  return (
    <section className={`panel data-panel ${className}`}>
      {(title || action) && (
        <div className="panel-heading">
          <div>
            {title && <h3>{title}</h3>}
            {subtitle && <p>{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
