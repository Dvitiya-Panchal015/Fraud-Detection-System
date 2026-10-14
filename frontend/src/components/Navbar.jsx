import React, { useState } from "react";
import { Bell, Menu, Radio, Search } from "lucide-react";
import { API_ORIGIN } from "../api/axios.js";

export default function Navbar({ title, onMenuClick, onNavigate, onSearch }) {
  const [search, setSearch] = useState("");

  function submitSearch(event) {
    event.preventDefault();
    onSearch(search.trim());
  }

  return (
    <header className="topbar">
      <button
        className="mobile-menu icon-button"
        onClick={onMenuClick}
        aria-label="Open navigation"
      >
        <Menu size={20} />
      </button>
      <div>
        <p className="topbar-overline">FRAUD DETECTION PLATFORM</p>
        <h1>{title}</h1>
        <p className="developer-attribution">Developed by Dvitiya Panchal</p>
      </div>
      <div className="topbar-actions">
        <form className="topbar-search" role="search" onSubmit={submitSearch}>
          <Search size={16} aria-hidden="true" />
          <input
            type="search"
            placeholder="Search transactions"
            aria-label="Search transactions"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <button type="submit" aria-label="Submit transaction search">
            <Search size={15} />
          </button>
        </form>
        <button
          className="topbar-icon-button"
          type="button"
          onClick={() => onNavigate("alerts")}
          aria-label="Open fraud alerts"
          title="Fraud alerts"
        >
          <Bell size={18} />
        </button>
        <div className="topbar-profile" title="Developed by Dvitiya Panchal">
          <span className="profile-avatar" aria-hidden="true">
            DP
          </span>
          <span className="profile-name">Dvitiya Panchal</span>
        </div>
        <a
          className="docs-button"
          href={`${API_ORIGIN}/docs`}
          target="_blank"
          rel="noreferrer"
        >
          <Radio size={15} />
          API docs
        </a>
      </div>
    </header>
  );
}