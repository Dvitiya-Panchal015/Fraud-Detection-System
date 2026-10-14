import React, { useState } from "react";
import { ArrowRight, CircleAlert, RotateCcw, ShieldCheck } from "lucide-react";
import { predictTransaction } from "../api/predictionApi.js";
import PageHeader from "../components/PageHeader.jsx";
import Panel from "../components/Panel.jsx";

const emptyForm = {
  step: "",
  transaction_type: "PAYMENT",
  amount: "",
  old_balance_origin: "",
  new_balance_origin: "",
  old_balance_destination: "",
  new_balance_destination: "",
};

const exampleForm = {
  ...emptyForm,
  step: "262",
  transaction_type: "PAYMENT",
  amount: "4880.94",
  old_balance_origin: "14308.44",
  new_balance_origin: "9427.5",
  old_balance_destination: "0",
  new_balance_destination: "0",
};

const numericFields = [
  ["step", "Time step (hours)", "1", "Enter step"],
  ["amount", "Transaction amount (INR)", "any", "Enter amount in INR"],
  [
    "old_balance_origin",
    "Origin balance before (INR)",
    "any",
    "Starting balance in INR",
  ],
  [
    "new_balance_origin",
    "Origin balance after (INR)",
    "any",
    "Ending balance in INR",
  ],
  [
    "old_balance_destination",
    "Destination balance before (INR)",
    "any",
    "Starting balance in INR",
  ],
  [
    "new_balance_destination",
    "Destination balance after (INR)",
    "any",
    "Ending balance in INR",
  ],
];

export default function PredictFraud() {
  const [form, setForm] = useState(exampleForm);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
    setResult(null);
    setError("");
  }

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    const transaction = { ...form };
    for (const [field] of numericFields) {
      transaction[field] = Number(form[field]);
    }

    try {
      setResult(await predictTransaction(transaction));
    } catch (requestError) {
      setError(requestError.message || "The transaction could not be scored.");
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setForm(emptyForm);
    setResult(null);
    setError("");
  }

  return (
    <>
      <PageHeader
        eyebrow="REAL-TIME SCORING"
        title="Predict fraud"
        description="Score a transaction with the trained PaySim model."
      />
      <div className="prediction-grid">
        <Panel
          title="Transaction details"
          subtitle="Pre-filled with a real PaySim test transaction. Edit the values or select Clear to start over."
        >
          <form onSubmit={submit}>
            <div className="form-grid">
              {numericFields.map(([name, label, step, placeholder]) => (
                <label className="field-label" key={name}>
                  {label}
                  <input
                    name={name}
                    type="number"
                    min="0"
                    step={step}
                    placeholder={placeholder}
                    value={form[name]}
                    onChange={updateField}
                    required
                  />
                </label>
              ))}
              <label className="field-label">
                Transaction type
                <select
                  name="transaction_type"
                  value={form.transaction_type}
                  onChange={updateField}
                  required
                >
                  {["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"].map(
                    (type) => (
                      <option key={type} value={type}>
                        {type.replaceAll("_", " ")}
                      </option>
                    ),
                  )}
                </select>
              </label>
            </div>
            {error && (
              <div className="inline-error" role="alert">
                <CircleAlert size={17} />
                <span>{error}</span>
              </div>
            )}
            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={loading}>
                {loading ? "Scoring transaction..." : "Run fraud check"}
                {!loading && <ArrowRight size={17} />}
              </button>
              <button className="secondary-button" type="button" onClick={reset}>
                <RotateCcw size={15} />
                Clear
              </button>
            </div>
          </form>
        </Panel>

        <Panel
          title="Prediction result"
          subtitle="Results are produced by the loaded model API."
          className="prediction-result-panel"
        >
          {!result && !error && (
            <div className="empty-result">
              <span className="result-shield">
                <ShieldCheck size={27} />
              </span>
              <strong>Ready to assess</strong>
              <p>Complete the transaction form to see its fraud risk score.</p>
            </div>
          )}
          {result && (
            <div className="prediction-result" aria-live="polite">
              <span
                className={`result-status ${
                  result.prediction === 1 ? "status-fraud" : "status-safe"
                }`}
              >
                {result.prediction === 1 ? "Potential fraud" : "Legitimate"}
              </span>
              <p>{result.message}</p>
              <div className="probability-value">
                {(result.fraud_probability * 100).toFixed(2)}
                <span>%</span>
              </div>
              <p className="muted">Fraud probability</p>
              <div className="probability-track">
                <div
                  className={
                    result.prediction === 1 ? "probability-high" : "probability-low"
                  }
                  style={{ width: `${result.fraud_probability * 100}%` }}
                />
              </div>
              <div className="threshold-line">
                <span>Decision threshold</span>
                <strong>{(result.threshold * 100).toFixed(0)}%</strong>
              </div>
              <p className="source-note">
                Prediction uses the model probability and the configured decision
                threshold.
              </p>
            </div>
          )}
        </Panel>
      </div>
    </>
  );
}