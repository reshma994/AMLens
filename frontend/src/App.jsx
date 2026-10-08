import { useEffect, useState } from "react";

import {
  getAnalysis,
  updateAlert,
  uploadCsv,
} from "./api";

import UploadPanel from "./components/UploadPanel";
import AlertList from "./components/AlertList";
import NetworkGraph from "./components/NetworkGraph";
import AccountPanel from "./components/AccountPanel";


function App() {
  const [analysis, setAnalysis] = useState(null);

  const [selectedAccount, setSelectedAccount] =
    useState(null);

  const [selectedAlert, setSelectedAlert] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [statusSaving, setStatusSaving] =
    useState(false);


  /*
  |--------------------------------------------------------------------------
  | Load analysis from URL
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    const params = new URLSearchParams(
      window.location.search
    );

    const analysisId =
      params.get("analysis");

    if (!analysisId) {
      return;
    }

    async function loadExistingAnalysis() {
      try {
        setLoading(true);
        setError("");

        const result =
          await getAnalysis(analysisId);

        setAnalysis(result);

      } catch (err) {
        setError(
          err.message ||
          "Unable to load the requested analysis."
        );

      } finally {
        setLoading(false);
      }
    }

    loadExistingAnalysis();
  }, []);


  /*
  |--------------------------------------------------------------------------
  | Upload
  |--------------------------------------------------------------------------
  */

  async function handleUpload(file) {
    try {
      setLoading(true);
      setError("");

      const result =
        await uploadCsv(file);

      setAnalysis(result);

      setSelectedAccount(null);
      setSelectedAlert(null);

      const url =
        new URL(window.location.href);

      url.searchParams.set(
        "analysis",
        result.analysis_id
      );

      window.history.pushState(
        {},
        "",
        url
      );

    } catch (err) {
      setError(
        err.message ||
        "Unable to process the transaction file."
      );

    } finally {
      setLoading(false);
    }
  }


  /*
  |--------------------------------------------------------------------------
  | Alert selection
  |--------------------------------------------------------------------------
  */

  function handleSelectAlert(alert) {
    setSelectedAlert(alert);
    setSelectedAccount(
      alert.account_id
    );
  }


  /*
  |--------------------------------------------------------------------------
  | Account selection
  |--------------------------------------------------------------------------
  */

  function handleSelectAccount(accountId) {
    setSelectedAccount(accountId);

    const matchingAlert =
      analysis?.alerts?.find(
        (alert) =>
          alert.account_id === accountId
      );

    setSelectedAlert(
      matchingAlert || null
    );
  }


  /*
  |--------------------------------------------------------------------------
  | Update review status
  |--------------------------------------------------------------------------
  */

  async function handleStatusChange(status) {
    if (
      !analysis ||
      !selectedAlert
    ) {
      return;
    }

    try {
      setStatusSaving(true);
      setError("");

      const updated =
        await updateAlert(
          analysis.analysis_id,
          selectedAlert.id,
          status
        );

      setAnalysis((previous) => ({
        ...previous,

        alerts:
          previous.alerts.map(
            (alert) =>
              alert.id === updated.id
                ? {
                    ...alert,
                    status:
                      updated.status,
                    updated_at:
                      updated.updated_at,
                  }
                : alert
          ),
      }));

      setSelectedAlert((previous) => ({
        ...previous,
        status: updated.status,
        updated_at:
          updated.updated_at,
      }));

    } catch (err) {
      setError(
        err.message ||
        "Unable to update alert status."
      );

    } finally {
      setStatusSaving(false);
    }
  }


  const selectedAccountData =
    analysis?.accounts?.find(
      (account) =>
        account.account_id ===
        selectedAccount
    );


  return (
    <div className="app-shell">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-mark">
            A
          </div>

          <div>
            <h1>AMLens</h1>

            <span>
              Transaction Intelligence
            </span>
          </div>

        </div>


        <div className="topbar-right">

          <div className="system-status">

            <span className="status-dot" />

            Investigation Engine Online

          </div>


          <div className="engine-version">
            RULES-V1
          </div>

        </div>

      </header>


      {/* =====================================================
          WORKSPACE
      ===================================================== */}

      <main className="workspace">


        {/* Page heading */}

        <section className="page-heading">

          <div>

            <div className="eyebrow">
              INVESTIGATION WORKSPACE
            </div>

            <h2>
              Transaction Network Analysis
            </h2>

            <p>
              Identify suspicious transaction patterns
              and investigate supporting evidence.
            </p>

          </div>


          <div className="analysis-indicator">

            <span>
              ANALYSIS
            </span>

            <strong>
              {analysis?.analysis_id ||
                "NOT LOADED"}
            </strong>

          </div>

        </section>


        {/* Error */}

        {error && (
          <div className="error-banner">

            <div>
              <strong>
                Analysis error
              </strong>

              <span>
                {error}
              </span>
            </div>

            <button
              onClick={() => setError("")}
            >
              Dismiss
            </button>

          </div>
        )}


        {/* Upload */}

        <UploadPanel
          onUpload={handleUpload}
          loading={loading}
        />


        {/* Summary */}

        <section className="summary-grid">

          <MetricCard
            label="TRANSACTIONS"
            value={
              analysis?.summary
                ?.total_transactions ??
              "--"
            }
            caption="Analysed transactions"
          />


          <MetricCard
            label="ACCOUNTS"
            value={
              analysis?.summary
                ?.total_accounts ??
              "--"
            }
            caption="Unique accounts"
          />


          <MetricCard
            label="ALERTS"
            value={
              analysis?.summary
                ?.alert_count ??
              "--"
            }
            caption="Flagged accounts"
            variant="alert"
          />


          <MetricCard
            label="HIGH RISK"
            value={
              analysis?.summary
                ?.high_risk_accounts ??
              "--"
            }
            caption="High + critical accounts"
            variant="critical"
          />

        </section>


        {/* =================================================
            MAIN INVESTIGATION
        ================================================= */}

        <section className="investigation-grid">


          {/* Alerts */}

          <aside className="alerts-column">

            <AlertList
              alerts={
                analysis?.alerts ?? []
              }

              accounts={
                analysis?.accounts ?? []
              }

              selectedAlert={
                selectedAlert
              }

              onSelectAlert={
                handleSelectAlert
              }
            />

          </aside>


          {/* Graph */}

          <section className="graph-column">

            <NetworkGraph
              graph={
                analysis?.graph
              }

              accounts={
                analysis?.accounts ?? []
              }

              selectedAccount={
                selectedAccount
              }

              onSelectAccount={
                handleSelectAccount
              }
            />

          </section>


          {/* Evidence */}

          <aside className="evidence-column">

            <AccountPanel
              account={
                selectedAccountData
              }

              selectedAlert={
                selectedAlert
              }

              onStatusChange={
                handleStatusChange
              }

              statusSaving={
                statusSaving
              }
            />

          </aside>


        </section>

      </main>

    </div>
  );
}


/*
|--------------------------------------------------------------------------
| Metric Card
|--------------------------------------------------------------------------
*/

function MetricCard({
  label,
  value,
  caption,
  variant = "",
}) {
  return (
    <div className="metric-card">

      <span className="metric-label">
        {label}
      </span>

      <strong
        className={
          variant
            ? `metric-${variant}`
            : ""
        }
      >
        {value}
      </strong>

      <span className="metric-caption">
        {caption}
      </span>

    </div>
  );
}


export default App;