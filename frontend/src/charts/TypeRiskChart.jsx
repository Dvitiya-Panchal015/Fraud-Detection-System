import React from "react";

export default function TypeRiskChart({ data }) {
  const maximum = Math.max(...data.map((item) => item.fraud_rate), 0.01);

  return (
    <div className="type-chart">
      {data.map((item) => (
        <div className="type-row" key={item.transaction_type}>
          <span>{item.transaction_type.replaceAll("_", " ")}</span>
          <div className="bar-track">
            <div
              className="bar-fill"
              style={{
                width: `${Math.max((item.fraud_rate / maximum) * 100, 1)}%`,
              }}
            />
          </div>
          <strong>{(item.fraud_rate * 100).toFixed(2)}%</strong>
        </div>
      ))}
      <p className="chart-note">
        Fraud rate by transaction type from the saved PaySim report.
      </p>
    </div>
  );
}
