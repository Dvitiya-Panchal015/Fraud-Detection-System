import React from "react";
import { Moon, Sun } from "lucide-react";
import PageHeader from "../components/PageHeader.jsx";
import Panel from "../components/Panel.jsx";

export default function Settings({ theme, onThemeChange }) {
  return (
    <>
      <PageHeader
        eyebrow="PREFERENCES"
        title="Settings"
        description="Project information and developer details."
      />
      <Panel title="Project information">
        <dl className="settings-info-list">
          <div>
            <dt>Project</dt>
            <dd>FraudGuard · PaySim Fraud Analytics</dd>
          </div>
          <div>
            <dt>Developer</dt>
            <dd>Developed by Dvitiya Panchal</dd>
          </div>
        </dl>
        <section className="theme-setting" aria-labelledby="theme-setting-title">
          <div className="theme-setting-heading">
            <h4 id="theme-setting-title">Appearance</h4>
            <p>Choose the dashboard color theme.</p>
          </div>
          <div className="theme-options" role="group" aria-label="Color theme">
            <button
              className={`theme-option ${theme === "light" ? "theme-option-active" : ""}`}
              type="button"
              aria-pressed={theme === "light"}
              onClick={() => onThemeChange("light")}
            >
              <Sun size={16} />
              Light Mode
            </button>
            <button
              className={`theme-option ${theme === "dark" ? "theme-option-active" : ""}`}
              type="button"
              aria-pressed={theme === "dark"}
              onClick={() => onThemeChange("dark")}
            >
              <Moon size={16} />
              Dark Mode
            </button>
          </div>
        </section>
      </Panel>
    </>
  );
}
