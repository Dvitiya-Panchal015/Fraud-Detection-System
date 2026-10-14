
import React, { useLayoutEffect, useState } from "react";
import Analytics from "./pages/Analytics.jsx";
import Alerts from "./pages/Alerts.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Monitoring from "./pages/Monitoring.jsx";
import PredictFraud from "./pages/PredictFraud.jsx";
import Settings from "./pages/Settings.jsx";
import Transactions from "./pages/Transactions.jsx";
import Navbar from "./components/Navbar.jsx";
import Sidebar from "./components/Sidebar.jsx";

const pageTitles = {
  dashboard: "Dashboard",
  alerts: "Fraud Alerts",
  predict: "Predict Fraud",
  transactions: "Transactions",
  analytics: "Analytics",
  monitoring: "Model Monitoring",
  settings: "Settings",
};

const THEME_STORAGE_KEY = "fraudguard-theme";

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [transactionSearch, setTransactionSearch] = useState("");
  const [theme, setTheme] = useState(
    () =>
      window.localStorage.getItem(THEME_STORAGE_KEY) === "dark"
        ? "dark"
        : "light",
  );

  useLayoutEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  function searchTransactions(query) {
    setTransactionSearch(query);
    setActivePage("transactions");
  }

  const pageComponents = {
    dashboard: <Dashboard onNavigate={setActivePage} />,
    alerts: <Alerts />,
    predict: <PredictFraud />,
    transactions: <Transactions initialSearch={transactionSearch} />,
    analytics: <Analytics />,
    monitoring: <Monitoring />,
    settings: <Settings theme={theme} onThemeChange={setTheme} />,
  };

  return (
    <div className="app-shell">
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <div className="main-shell">
        <Navbar
          title={pageTitles[activePage]}
          onMenuClick={() => setSidebarOpen(true)}
          onNavigate={setActivePage}
          onSearch={searchTransactions}
        />
        <main className="content-area" key={activePage}>
          {pageComponents[activePage]}
        </main>
      </div>
    </div>
  );
}
