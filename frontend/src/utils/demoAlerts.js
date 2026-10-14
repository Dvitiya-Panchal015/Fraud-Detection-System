import { getAlertRiskLevel } from "./alertConfig.js";

export const ALERT_STATUS_STORAGE_KEY = "fraud-alert-demo-status-v1";

export const demoAlerts = [
  {
    transactionId: "DEMO-TXN-10482",
    amount: 12450.0,
    fraudProbability: 0.96,
    timestamp: new Date(Date.now() - 8 * 60_000).toISOString(),
    status: "New",
  },
  {
    transactionId: "DEMO-TXN-10479",
    amount: 8750.5,
    fraudProbability: 0.84,
    timestamp: new Date(Date.now() - 34 * 60_000).toISOString(),
    status: "Reviewed",
  },
  {
    transactionId: "DEMO-TXN-10473",
    amount: 3180.0,
    fraudProbability: 0.72,
    timestamp: new Date(Date.now() - 82 * 60_000).toISOString(),
    status: "New",
  },
  {
    transactionId: "DEMO-TXN-10468",
    amount: 642.25,
    fraudProbability: 0.58,
    timestamp: new Date(Date.now() - 145 * 60_000).toISOString(),
    status: "Reviewed",
  },
  {
    transactionId: "DEMO-TXN-10461",
    amount: 2099.99,
    fraudProbability: 0.43,
    timestamp: new Date(Date.now() - 230 * 60_000).toISOString(),
    status: "Resolved",
  },
  {
    transactionId: "DEMO-TXN-10455",
    amount: 185.75,
    fraudProbability: 0.18,
    timestamp: new Date(Date.now() - 315 * 60_000).toISOString(),
    status: "New",
  },
  {
    transactionId: "DEMO-TXN-10449",
    amount: 960.0,
    fraudProbability: 0.08,
    timestamp: new Date(Date.now() - 440 * 60_000).toISOString(),
    status: "Resolved",
  },
];

const alertStatuses = new Set(["New", "Reviewed", "Resolved"]);

export function loadDemoAlertState() {
  try {
    const storedStatuses = window.sessionStorage.getItem(
      ALERT_STATUS_STORAGE_KEY,
    );
    if (!storedStatuses) {
      return { alerts: demoAlerts, persistenceWarning: "" };
    }

    const statuses = JSON.parse(storedStatuses);
    if (
      !statuses ||
      typeof statuses !== "object" ||
      Array.isArray(statuses) ||
      Object.entries(statuses).some(
        ([transactionId, status]) =>
          !demoAlerts.some((alert) => alert.transactionId === transactionId) ||
          !alertStatuses.has(status),
      )
    ) {
      throw new Error("saved demo alert statuses are invalid");
    }

    return {
      alerts: demoAlerts.map((alert) => ({
        ...alert,
        status: statuses[alert.transactionId] ?? alert.status,
      })),
      persistenceWarning: "",
    };
  } catch (error) {
    return {
      alerts: demoAlerts,
      persistenceWarning: `Could not restore review statuses in this browser tab: ${error.message}`,
    };
  }
}

export function countUnresolvedHighRiskAlerts(alerts) {
  return alerts.filter(
    (alert) =>
      getAlertRiskLevel(alert.fraudProbability) === "High" &&
      alert.status !== "Resolved",
  ).length;
}
