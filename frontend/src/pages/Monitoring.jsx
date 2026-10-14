import React, { useCallback, useEffect, useState } from "react";
import {
  Activity,
  CircleCheck,
  CircleHelp,
  Database,
  Gauge,
  Shield,
} from "lucide-react";
import { getMonitoring } from "../api/monitoringApi.js";
import ErrorMessage from "../components/ErrorMessage.jsx";
import Loading from "../components/Loading.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Panel from "../components/Panel.jsx";

function Status({ available, label }) {
  return (
    <span className={`monitor-status ${available ? "monitor-ok" : "monitor-off"}`}>
      {available ? <CircleCheck size={15} /> : <CircleHelp size={15} />}
      {label}
    </span>
  );
}

export default function Monitoring() {
  const [monitoring, setMonitoring] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setMonitoring(await getMonitoring());
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
        eyebrow="SYSTEM STATUS"
        title="Model monitoring"
        description="Availability and tracking status from the running API and project artifacts."
        action={
          <button className="secondary-button" onClick={load} disabled={loading}>
            <Activity size={15} />
            Refresh
          </button>
        }
      />
      {loading && <Loading label="Checking API, model, and MLflow..." />}
      {error && <ErrorMessage message={error} onRetry={load} />}
      {monitoring && !loading && (
        <>
          <div className="monitor-grid">
            <Panel title="API health" subtitle="Current backend process response">
              <div className="monitor-value-row">
                <Activity size={20} />
                <Status
                  available={monitoring.health.status === "healthy"}
                  label={
                    monitoring.health.status === "healthy"
                      ? "Healthy"
                      : "Unavailable"
                  }
                />
              </div>
              <p className="monitor-detail">
                {monitoring.health.service || "Fraud detection API"}
              </p>
            </Panel>
            <Panel title="Model artifact" subtitle="Configured prediction model">
              <div className="monitor-value-row">
                <Shield size={20} />
                <Status
                  available={monitoring.model.available && monitoring.health.model_ready}
                  label={
                    monitoring.model.available && monitoring.health.model_ready
                      ? "Loaded"
                      : "Not configured"
                  }
                />
              </div>
              <p className="monitor-detail mono-text">{monitoring.model.artifact}</p>
            </Panel>
            <Panel title="Decision threshold" subtitle="Selected from saved tuning results">
              <div className="monitor-value-row">
                <Gauge size={20} />
                <Status
                  available={monitoring.threshold.available}
                  label={
                    monitoring.threshold.available
                      ? `${(monitoring.threshold.value * 100).toFixed(0)}%`
                      : "Not configured"
                  }
                />
              </div>
              <p className="monitor-detail">
                {monitoring.threshold.available
                  ? "Maximum-F1 validation threshold"
                  : monitoring.threshold.message}
              </p>
            </Panel>
            <Panel
              title="Data drift"
              subtitle="Training-vs-test PSI comparison (not live monitoring)"
            >
              <div className="monitor-value-row">
                <Database size={20} />
                <Status
                  available={monitoring.data_drift.available}
                  label={
                    monitoring.data_drift.available
                      ? `${monitoring.data_drift.status} PSI`
                      : "Not available"
                  }
                />
              </div>
              <p className="monitor-detail">{monitoring.data_drift.message}</p>
            </Panel>
          </div>

          <Panel
            title="MLflow validation metrics"
            subtitle={
              monitoring.mlflow.available
                ? `${monitoring.mlflow.experiment} · latest completed run ${monitoring.mlflow.run_id}`
                : monitoring.mlflow.message
            }
          >
            {monitoring.mlflow.available ? (
              <div className="evaluation-metrics">
                {Object.entries(monitoring.mlflow.metrics).map(([key, value]) => (
                  <div key={key}>
                    <span>{key.replaceAll("_", " ")}</span>
                    <strong>{value.toFixed(4)}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">{monitoring.mlflow.message}</p>
            )}
          </Panel>
          {monitoring.data_drift.available && (
            <Panel
              title="Training vs test feature drift"
              subtitle={`PSI comparison · ${monitoring.data_drift.reference_sample_size.toLocaleString()} training rows vs ${monitoring.data_drift.current_sample_size.toLocaleString()} test rows`}
              className="drift-panel"
            >
              <div className="drift-list">
                {monitoring.data_drift.features.map((feature) => (
                  <div className="drift-row" key={feature.feature}>
                    <div className="drift-feature">
                      <strong>{feature.feature.replaceAll("_", " ")}</strong>
                      <span>{feature.data_type}</span>
                    </div>
                    <div
                      className="bar-track drift-track"
                      role="img"
                      aria-label={`${feature.feature} PSI ${feature.psi.toFixed(4)}`}
                    >
                      <div
                        className={`bar-fill drift-fill drift-${feature.status}`}
                        style={{
                          width: `${Math.min((feature.psi / 0.5) * 100, 100)}%`,
                        }}
                      />
                    </div>
                    <strong className="drift-score">{feature.psi.toFixed(4)}</strong>
                    <span className={`drift-badge drift-badge-${feature.status}`}>
                      {feature.status}
                    </span>
                  </div>
                ))}
              </div>
              <p className="source-note">
                {monitoring.data_drift.reference} → {monitoring.data_drift.current}.
                {` ${monitoring.data_drift.interpretation}`}
              </p>
              <p className="source-note">{monitoring.data_drift.message}</p>
            </Panel>
          )}
          <p className="source-note">
            Monitoring reflects local files and the configured local MLflow
            tracking database. The PSI table compares saved training and test
            samples; live production drift monitoring is not configured.
          </p>
        </>
      )}
    </>
  );
}