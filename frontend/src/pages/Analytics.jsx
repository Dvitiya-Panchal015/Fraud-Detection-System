import React, { useCallback, useEffect, useState } from "react";
import { getAnalytics } from "../api/analyticsApi.js";
import ErrorMessage from "../components/ErrorMessage.jsx";
import Loading from "../components/Loading.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Panel from "../components/Panel.jsx";
import StatCard from "../components/StatCard.jsx";
import TypeRiskChart from "../charts/TypeRiskChart.jsx";
import { Activity, BadgeCheck, Crosshair, Gauge } from "lucide-react";

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setAnalytics(await getAnalytics());
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <>
      <PageHeader
        eyebrow="MODEL QUALITY"
        title="Analytics"
        description="Evaluation metrics and fraud patterns from saved project artifacts."
      />
      {loading && <Loading label="Loading evaluation reports..." />}
      {error && <ErrorMessage message={error} onRetry={load} />}
      {analytics && !loading && (
        <>
          <div className="stat-grid analytics-stat-grid">
            <StatCard
              label="Precision"
              value={analytics.test_evaluation.precision.toFixed(4)}
              detail="Held-out test set"
              icon={Crosshair}
              tone="violet"
            />
            <StatCard
              label="Recall"
              value={analytics.test_evaluation.recall.toFixed(4)}
              detail="Held-out test set"
              icon={Activity}
              tone="green"
            />
            <StatCard
              label="F1 score"
              value={analytics.test_evaluation.f1.toFixed(4)}
              detail="Held-out test set"
              icon={BadgeCheck}
            />
            <StatCard
              label="ROC-AUC"
              value={analytics.test_evaluation.roc_auc.toFixed(4)}
              detail="Held-out test set"
              icon={Gauge}
              tone="amber"
            />
          </div>
          <div className="dashboard-grid">
            <Panel
              title="Fraud rate by transaction type"
              subtitle="Fraud percentage from the saved PaySim report"
            >
              <TypeRiskChart data={analytics.fraud_rates_by_type} />
              <p className="source-note">{analytics.dataset.source}</p>
            </Panel>
            <Panel
              title="Test confusion matrix"
              subtitle={`${analytics.test_evaluation.test_transactions.toLocaleString()} held-out records · threshold ${(analytics.test_evaluation.threshold * 100).toFixed(0)}%`}
            >
              <div className="matrix-table">
                <div className="matrix-corner" />
                <strong>Predicted legitimate</strong>
                <strong>Predicted fraud</strong>
                <strong>Actual legitimate</strong>
                <span className="matrix-tn">
                  {analytics.confusion_matrix.actual_legitimate[0].toLocaleString()}
                </span>
                <span className="matrix-fp">
                  {analytics.confusion_matrix.actual_legitimate[1].toLocaleString()}
                </span>
                <strong>Actual fraud</strong>
                <span className="matrix-fn">
                  {analytics.confusion_matrix.actual_fraud[0].toLocaleString()}
                </span>
                <span className="matrix-tp">
                  {analytics.confusion_matrix.actual_fraud[1].toLocaleString()}
                </span>
              </div>
              <div className="matrix-legend">
                <span>Correct classification</span>
                <span>Incorrect classification</span>
              </div>
            </Panel>
          </div>
          <Panel
            title="Additional test metrics"
            subtitle={analytics.test_evaluation.source}
          >
            <div className="evaluation-metrics">
              {[
                ["Average precision (PR-AUC)", analytics.test_evaluation.average_precision],
                ["Decision threshold", analytics.test_evaluation.threshold],
                ["Actual fraud examples", analytics.test_evaluation.actual_fraud_transactions],
                ["Test records", analytics.test_evaluation.test_transactions],
              ].map(([label, value]) => (
                <div key={label}>
                  <span>{label}</span>
                  <strong>
                    {typeof value === "number" && value < 1
                      ? value.toFixed(4)
                      : Number(value).toLocaleString()}
                  </strong>
                </div>
              ))}
            </div>
          </Panel>
        </>
      )}
    </>
  );
}