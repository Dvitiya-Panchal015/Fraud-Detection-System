import React from "react";
import {
  Activity,
  BellRing,
  ChartNoAxesCombined,
  LayoutDashboard,
  ListFilter,
  ScanSearch,
  Settings as SettingsIcon,
  ShieldCheck,
} from "lucide-react";

const links = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "alerts", label: "Fraud Alerts", icon: BellRing },
  { id: "predict", label: "Predict Fraud", icon: ScanSearch },
  { id: "transactions", label: "Transactions", icon: ListFilter },
  { id: "analytics", label: "Analytics", icon: ChartNoAxesCombined },
  { id: "monitoring", label: "Model Monitoring", icon: Activity },
  { id: "settings", label: "Settings", icon: SettingsIcon },
];

export default function Sidebar({ activePage, onNavigate, open, onClose }) {
  return (
    <>
      {open && (
        <button
          className="sidebar-backdrop"
          aria-label="Close navigation"
          onClick={onClose}
        />
      )}
      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="brand">
          <span className="brand-mark">
            <ShieldCheck size={21} />
          </span>
          <span>
            <strong>FraudGuard</strong>
            <small className="brand-developer">Developed by Dvitiya Panchal</small>
          </span>
        </div>
        <p className="nav-caption">WORKSPACE</p>
        <nav aria-label="Main navigation">
          {links.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`nav-link ${activePage === id ? "nav-active" : ""}`}
              onClick={() => {
                onNavigate(id);
                onClose();
              }}
              aria-current={activePage === id ? "page" : undefined}
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </aside>
    </>
  );
}