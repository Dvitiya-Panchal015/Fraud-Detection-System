function readThreshold(value, name, fallback) {
  const configuredValue = value?.trim();
  if (!configuredValue) {
    return fallback;
  }

  const threshold = Number(configuredValue);
  if (!Number.isFinite(threshold) || threshold < 0 || threshold > 1) {
    throw new Error(`${name} must be a number from 0 to 1.`);
  }
  return threshold;
}

export const MEDIUM_RISK_THRESHOLD = readThreshold(
  import.meta.env.VITE_ALERT_MEDIUM_RISK_THRESHOLD,
  "VITE_ALERT_MEDIUM_RISK_THRESHOLD",
  0.3,
);
export const HIGH_RISK_THRESHOLD = readThreshold(
  import.meta.env.VITE_ALERT_HIGH_RISK_THRESHOLD,
  "VITE_ALERT_HIGH_RISK_THRESHOLD",
  0.7,
);

if (HIGH_RISK_THRESHOLD <= MEDIUM_RISK_THRESHOLD) {
  throw new Error(
    "VITE_ALERT_HIGH_RISK_THRESHOLD must be greater than VITE_ALERT_MEDIUM_RISK_THRESHOLD.",
  );
}

export function getAlertRiskLevel(probability) {
  if (!Number.isFinite(probability) || probability < 0 || probability > 1) {
    throw new RangeError("Fraud probability must be a number from 0 to 1.");
  }

  if (probability >= HIGH_RISK_THRESHOLD) {
    return "High";
  }
  if (probability >= MEDIUM_RISK_THRESHOLD) {
    return "Medium";
  }
  return "Low";
}
