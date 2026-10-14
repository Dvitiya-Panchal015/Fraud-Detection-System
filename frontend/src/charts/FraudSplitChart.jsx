import React from "react";

const numberFormat = new Intl.NumberFormat("en-US");

export default function FraudSplitChart({ fraud, legitimate }) {
  const total = fraud + legitimate;
  const fraudPercent = total ? (fraud / total) * 100 : 0;
  const ring = `conic-gradient(var(--red) 0 ${fraudPercent}%, var(--cyan) ${fraudPercent}% 100%)`;

  return (
    <div className="split-chart">
      <div
        className="donut-chart"
        style={{ background: ring }}
        role="img"
        aria-label={`${fraudPercent.toFixed(3)} percent fraud in the full dataset`}
      >
        <div>
          <strong>{fraudPercent.toFixed(2)}%</strong>
          <span>fraud rate</span>
        </div>
      </div>
      <div className="chart-legend">
        <div>
          <span className="legend-dot legend-cyan" />
          <span>Legitimate</span>
          <strong>{numberFormat.format(legitimate)}</strong>
        </div>
        <div>
          <span className="legend-dot legend-red" />
          <span>Fraud</span>
          <strong>{numberFormat.format(fraud)}</strong>
        </div>
      </div>
    </div>
  );
}
