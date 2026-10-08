function AlertList({
  alerts,
  accounts,
  selectedAlert,
  onSelectAlert,
}) {
  return (
    <section className="panel">

      <div className="panel-header">

        <div>

          <h3>
            Risk Alerts
          </h3>

          <p>
            Ranked suspicious accounts
          </p>

        </div>

        {alerts.length > 0 && (
          <span className="panel-count">
            {alerts.length}
          </span>
        )}

      </div>


      {alerts.length === 0 ? (

        <div className="empty-state">

          <div>

            <strong>
              No analysis loaded
            </strong>

            <p>
              Load a dataset to view alerts.
            </p>

          </div>

        </div>

      ) : (

        <div className="alert-list">

          {alerts
            .map((alert) => {

              const account =
                accounts.find(
                  (item) =>
                    item.account_id ===
                    alert.account_id
                );


              const selected =
                selectedAlert?.id ===
                alert.id;


              return (
                <button
                  key={alert.id}
                  className={`alert-item ${
                    selected
                      ? "selected"
                      : ""
                  }`}
                  onClick={() =>
                    onSelectAlert(alert)
                  }
                >

                  <div className="alert-main">

                    <span className="alert-account">
                      {alert.account_id}
                    </span>


                    <span
                      className={`risk-badge ${
                        account?.risk_level?.toLowerCase() ||
                        "low"
                      }`}
                    >
                      {account?.risk_level ||
                        "LOW"}
                    </span>

                  </div>


                  <div className="alert-score">

                    <strong>
                      {account?.risk_score ??
                        0}
                    </strong>

                    <span>
                      / 100
                    </span>

                  </div>


                  <div className="alert-meta">

                    <span>
                      {alert.status}
                    </span>

                    <span>
                      {account?.reasons
                        ?.length ?? 0}{" "}
                      pattern
                      {account?.reasons
                        ?.length === 1
                        ? ""
                        : "s"}
                    </span>

                  </div>

                </button>
              );
            })}

        </div>

      )}

    </section>
  );
}


export default AlertList;