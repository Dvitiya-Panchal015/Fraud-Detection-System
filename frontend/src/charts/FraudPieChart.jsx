import React from "react";

const numberFormat = new Intl.NumberFormat("en-US");

export default function FraudPieChart({ fraud, legitimate }) {
  const total = fraud + legitimate;
  const legitimatePercent = total ? (legitimate / total) * 100 : 0;
  const fraudPercent = total ? (fraud / total) * 100 : 0;
  const pie = `conic-gradient(var(--green) 0 ${legitimatePercent}%, var(--red) ${legitimatePercent}% 100%)`;

  return (
    <div className="pie-chart-layout">
      <div
        className="pie-chart"
        style={{ background: pie }}
        role="img"
        aria-label={`${numberFormat.format(legitimate)} legitimate transactions (${legitimatePercent.toFixed(2)} percent) and ${numberFormat.format(fraud)} fraudulent transactions (${fraudPercent.toFixed(2)} percent)`}
      />
      <div className="pie-chart-legend">
        <div className="pie-chart-legend-row">
          <span className="legend-dot legend-green" />
          <span>Legitimate</span>
          <strong>{numberFormat.format(legitimate)}</strong>
          <small>{legitimatePercent.toFixed(2)}%</small>
        </div>
        <div className="pie-chart-legend-row">
          <span className="legend-dot legend-red" />
          <span>Fraudulent</span>
          <strong>{numberFormat.format(fraud)}</strong>
          <small>{fraudPercent.toFixed(2)}%</small>
        </div>
      </div>
    </div>
  );
}
