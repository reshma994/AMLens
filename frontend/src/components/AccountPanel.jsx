function AccountPanel({
  account,
  selectedAlert,
  onStatusChange,
  statusSaving,
}) {
  if (!account) {
    return (
      <section className="panel">

        <div className="panel-header">

          <div>

            <h3>
              Account Evidence
            </h3>

            <p>
              Investigation details
            </p>

          </div>

        </div>


        <div className="empty-state">

          <div>

            <div className="empty-icon">
              ◇
            </div>

            <strong>
              No account selected
            </strong>

            <p>
              Select a risk alert or graph node
              to inspect its evidence.
            </p>

          </div>

        </div>

      </section>
    );
  }


  const riskClass =
    account.risk_level.toLowerCase();


  return (
    <section className="panel account-panel">

      <div className="panel-header">

        <div>

          <h3>
            Account Evidence
          </h3>

          <p>
            Investigation details
          </p>

        </div>


        {selectedAlert && (
          <span
            className={`status-badge ${
              selectedAlert.status
                .toLowerCase()
                .replace("_", "-")
            }`}
          >
            {selectedAlert.status}
          </span>
        )}

      </div>


      <div className="account-content">


        {/* Account identity */}

        <div className="account-heading">

          <div>

            <span>
              ACCOUNT
            </span>

            <strong>
              {account.account_id}
            </strong>

          </div>


          <span
            className={`risk-badge ${riskClass}`}
          >
            {account.risk_level}
          </span>

        </div>


        {/* Score */}

        <div className="risk-score-block">

          <div>

            <span>
              RISK SCORE
            </span>

            <strong>
              {account.risk_score}
            </strong>

            <small>
              / 100 points
            </small>

          </div>


          <div className="score-bar">

            <div
              className={`score-fill ${riskClass}`}
              style={{
                width:
                  `${account.risk_score}%`,
              }}
            />

          </div>

        </div>


        {/* Evidence */}

        <div className="evidence-section">

          <div className="section-title">
            DETECTED PATTERNS
          </div>


          {account.reasons.length === 0 ? (

            <div className="no-pattern">

              <span>
                ✓
              </span>

              <div>

                <strong>
                  No configured pattern detected
                </strong>

                <p>
                  No configured suspicious pattern
                  contributed to this account's score.
                </p>

              </div>

            </div>

          ) : (

            account.reasons.map(
              (reason) => (

                <div
                  className="reason-card"
                  key={reason.code}
                >

                  <div className="reason-header">

                    <strong>
                      {formatReason(
                        reason.code
                      )}
                    </strong>

                    <span>
                      +{reason.points}
                    </span>

                  </div>


                  <p>
                    {reason.code ===
                    "CIRCULAR_FLOW"
                      ? "Time-ordered circular transfer"
                      : "Rapid incoming-to-outgoing transfer"}
                  </p>


                  <div className="transaction-list">

                    {reason.transaction_ids.map(
                      (transactionId) => (

                        <span
                          key={transactionId}
                        >
                          {transactionId}
                        </span>

                      )
                    )}

                  </div>

                </div>

              )
            )

          )}

        </div>


        {/* Review */}

        {selectedAlert && (

          <div className="review-section">

            <div className="section-title">
              REVIEW STATUS
            </div>


            <div className="review-buttons">

              <button
                className={
                  selectedAlert.status ===
                  "OPEN"
                    ? "review-button active"
                    : "review-button"
                }
                disabled={statusSaving}
                onClick={() =>
                  onStatusChange("OPEN")
                }
              >
                Open
              </button>


              <button
                className={
                  selectedAlert.status ===
                  "UNDER_REVIEW"
                    ? "review-button active"
                    : "review-button"
                }
                disabled={statusSaving}
                onClick={() =>
                  onStatusChange(
                    "UNDER_REVIEW"
                  )
                }
              >
                Under Review
              </button>


              <button
                className={
                  selectedAlert.status ===
                  "DISMISSED"
                    ? "review-button active"
                    : "review-button"
                }
                disabled={statusSaving}
                onClick={() =>
                  onStatusChange(
                    "DISMISSED"
                  )
                }
              >
                Dismissed
              </button>

            </div>

          </div>

        )}

      </div>

    </section>
  );
}


/*
|--------------------------------------------------------------------------
| Reason formatting
|--------------------------------------------------------------------------
*/

function formatReason(code) {
  if (code === "CIRCULAR_FLOW") {
    return "Circular Flow";
  }

  if (code === "RAPID_PASS_THROUGH") {
    return "Rapid Pass-Through";
  }

  return code
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    );
}


export default AccountPanel;