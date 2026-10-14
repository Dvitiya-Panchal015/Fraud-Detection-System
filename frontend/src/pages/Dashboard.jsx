import React, { useCallback, useEffect, useState } from "react";
import {
  Activity,
  BadgePercent,
  CircleDollarSign,
  ShieldCheck,
  ShieldAlert,
} from "lucide-react";
import { getAnalytics } from "../api/analyticsApi.js";
import ErrorMessage from "../components/ErrorMessage.jsx";
import Loading from "../components/Loading.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Panel from "../components/Panel.jsx";
import StatCard from "../components/StatCard.jsx";
import FraudSplitChart from "../charts/FraudSplitChart.jsx";
import FraudPieChart from "../charts/FraudPieChart.jsx";
import TypeRiskChart from "../charts/TypeRiskChart.jsx";
import HourlyVolumeChart from "../charts/HourlyVolumeChart.jsx";
import FraudAlertNotice from "../components/FraudAlertNotice.jsx";
import {
  countUnresolvedHighRiskAlerts,
  loadDemoAlertState,
} from "../utils/demoAlerts.js";

const numberFormat = new Intl.NumberFormat("en-US");

export default function Dashboard({ onNavigate }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [demoAlertState] = useState(loadDemoAlertState);
  const highRiskAlertCount = countUnresolvedHighRiskAlerts(demoAlertState.alerts);
  const currentDate = new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(new Date());

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
        eyebrow="OVERVIEW"
        title="Fraud operations"
        description="A data-backed view of your PaySim fraud detection project."
      />
      <section className="welcome-banner" aria-labelledby="welcome-title">
        <div className="welcome-copy">
          <p className="welcome-date">{currentDate}</p>
          <h2 id="welcome-title">Welcome back, Dvitiya! 👋</h2>
          <p>
            Monitor transactions, detect suspicious activity, and track fraud
            insights in one place.
          </p>
        </div>
        <span className="welcome-icon" aria-hidden="true">
          <ShieldCheck size={28} strokeWidth={1.7} />
        </span>
      </section>
      <FraudAlertNotice
        count={highRiskAlertCount}
        onClick={() => onNavigate("alerts")}
      />
      {demoAlertState.persistenceWarning && (
        <div className="alert-storage-warning" role="alert">
          {demoAlertState.persistenceWarning}
        </div>
      )}
      {loading && <Loading label="Loading dataset and evaluation artifacts..." />}
      {error && <ErrorMessage message={error} onRetry={load} />}
      {analytics && !loading && (
        <>
          <div className="stat-grid dashboard-stat-grid">
            <StatCard
              label="Total Transactions Analyzed"
              value={numberFormat.format(analytics.dataset.transaction_count)}
              detail="Full PaySim dataset"
              icon={CircleDollarSign}
            />
            <StatCard
              label="Fraud Transactions"
              value={numberFormat.format(analytics.dataset.fraud_count)}
              detail="Ground-truth dataset labels"
              icon={ShieldAlert}
              tone="red"
            />
            <StatCard
              label="Fraud rate"
              value={`${(analytics.dataset.fraud_rate * 100).toFixed(3)}%`}
              detail="Full dataset prevalence"
              icon={BadgePercent}
              tone="violet"
            />
            <StatCard
              label="High-Risk Alerts"
              value={numberFormat.format(highRiskAlertCount)}
              detail="Unresolved demo alerts"
              icon={ShieldAlert}
              tone="red"
            />
            <StatCard
              label="Test ROC-AUC"
              value={analytics.test_evaluation.roc_auc.toFixed(4)}
              detail="Saved holdout evaluation"
              icon={Activity}
              tone="green"
            />
          </div>
          <div className="dashboard-grid">
            <Panel
              title="Fraud vs legitimate"
              subtitle="Recorded labels across the full PaySim dataset"
              className="chart-panel"
            >
              <FraudSplitChart
                fraud={analytics.dataset.fraud_count}
                legitimate={analytics.dataset.legitimate_count}
              />
              <p className="source-note">{analytics.dataset.source}</p>
            </Panel>
            <Panel
              title="Fraud vs Legitimate Transactions"
              subtitle="Recorded transaction counts across the full PaySim dataset"
              className="chart-panel"
            >
              <FraudPieChart
                fraud={analytics.dataset.fraud_count}
                legitimate={analytics.dataset.legitimate_count}
              />
            </Panel>
            <Panel
              title="Fraud by transaction type"
              subtitle="Historical fraud rates from the saved dataset report"
              className="chart-panel"
            >
              <TypeRiskChart data={analytics.fraud_rates_by_type} />
            </Panel>
            <Panel
              title="Transaction volume by hour"
              subtitle="Illustrative 24-hour profile · demo data"
              className="chart-panel"
            >
              <HourlyVolumeChart />
            </Panel>
          </div>
          <Panel
            title="Model evaluation snapshot"
            subtitle="Measured on the saved held-out test set, not live predictions"
            className="evaluation-strip"
            action={
              <button
                className="secondary-button"
                onClick={() => onNavigate("analytics")}
              >
                Full analytics
              </button>
            }
          >
            <div className="evaluation-metrics">
              {[
                ["Precision", analytics.test_evaluation.precision],
                ["Recall", analytics.test_evaluation.recall],
                ["F1 score", analytics.test_evaluation.f1],
                ["Average precision", analytics.test_evaluation.average_precision],
              ].map(([label, value]) => (
                <div key={label}>
                  <span>{label}</span>
                  <strong>{Number(value).toFixed(4)}</strong>
                </div>
              ))}
            </div>
          </Panel>
        </>
      )}
    </>
  );
}