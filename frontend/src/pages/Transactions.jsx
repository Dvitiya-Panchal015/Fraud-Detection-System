import React, { useCallback, useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { getTransactions } from "../api/transactionApi.js";
import ErrorMessage from "../components/ErrorMessage.jsx";
import Loading from "../components/Loading.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Panel from "../components/Panel.jsx";
import { formatCurrency } from "../utils/formatters.js";

export default function Transactions({ initialSearch = "" }) {
  const [search, setSearch] = useState(initialSearch);
  const [filterType, setFilterType] = useState("");
  const [filterLabel, setFilterLabel] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const pageSize = 25;

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setData(
        await getTransactions({
          page,
          page_size: pageSize,
          search,
          transaction_type: filterType,
          is_fraud:
            filterLabel === "" ? undefined : filterLabel === "fraud",
        }),
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }, [filterLabel, filterType, page, search]);

  useEffect(() => {
    const timer = window.setTimeout(load, 250);
    return () => window.clearTimeout(timer);
  }, [load]);

  useEffect(() => {
    setSearch(initialSearch);
    setPage(1);
  }, [initialSearch]);

  function updateFilter(setter, value) {
    setter(value);
    setPage(1);
  }

  const pageCount = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;

  return (
    <>
      <PageHeader
        eyebrow="LABELED DATA"
        title="Transactions"
        description="Search and filter real records from the PaySim held-out test split."
      />
      <Panel
        title="Held-out transactions"
        subtitle={
          data
            ? `${data.total.toLocaleString()} matching labeled records`
            : "Loading saved test records..."
        }
        className="table-panel"
      >
        <div className="table-toolbar">
          <label className="search-field">
            <Search size={17} />
            <input
              type="search"
              placeholder="Search type or amount"
              value={search}
              onChange={(event) => updateFilter(setSearch, event.target.value)}
              aria-label="Search transactions"
            />
          </label>
          <select
            value={filterType}
            onChange={(event) => updateFilter(setFilterType, event.target.value)}
            aria-label="Filter transaction type"
          >
            <option value="">All transaction types</option>
            {["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"].map(
              (type) => (
                <option value={type} key={type}>
                  {type.replaceAll("_", " ")}
                </option>
              ),
            )}
          </select>
          <select
            value={filterLabel}
            onChange={(event) => updateFilter(setFilterLabel, event.target.value)}
            aria-label="Filter recorded label"
          >
            <option value="">All labels</option>
            <option value="fraud">Recorded fraud</option>
            <option value="legitimate">Recorded legitimate</option>
          </select>
        </div>
        {error && <ErrorMessage message={error} onRetry={load} />}
        {loading && <Loading label="Searching the held-out test split..." />}
        {!loading && !error && data && (
          <>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Holdout row</th>
                    <th>Step</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Origin before</th>
                    <th>Origin after</th>
                    <th>Destination before</th>
                    <th>Destination after</th>
                    <th>Recorded label</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((item) => (
                    <tr key={item.record_id}>
                      <td className="mono-text">{item.record_id}</td>
                      <td>{item.step}</td>
                      <td>{item.transaction_type.replaceAll("_", " ")}</td>
                      <td>{formatCurrency(item.amount)}</td>
                      <td>{formatCurrency(item.old_balance_origin)}</td>
                      <td>{formatCurrency(item.new_balance_origin)}</td>
                      <td>{formatCurrency(item.old_balance_destination)}</td>
                      <td>{formatCurrency(item.new_balance_destination)}</td>
                      <td>
                        <span
                          className={`label-badge ${
                            item.is_fraud ? "label-fraud" : "label-legitimate"
                          }`}
                        >
                          {item.is_fraud ? "Fraud" : "Legitimate"}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {data.items.length === 0 && (
                    <tr>
                      <td className="empty-cell" colSpan="9">
                        No records match these filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div className="table-footer">
              <p>{data.source}</p>
              <div className="pagination">
                <span>
                  Page {page} of {pageCount}
                </span>
                <button
                  className="icon-button"
                  aria-label="Previous page"
                  disabled={page <= 1 || loading}
                  onClick={() => setPage((current) => current - 1)}
                >
                  <ChevronLeft size={17} />
                </button>
                <button
                  className="icon-button"
                  aria-label="Next page"
                  disabled={page >= pageCount || loading}
                  onClick={() => setPage((current) => current + 1)}
                >
                  <ChevronRight size={17} />
                </button>
              </div>
            </div>
          </>
        )}
      </Panel>
    </>
  );
}