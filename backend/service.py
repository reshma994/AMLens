from datetime import datetime, timezone

from backend.database import save_analysis
from backend.ingestion import parse_csv


def get_analysis_engine():
    """
    Import Dev 1's analysis engine lazily.

    This keeps the backend independent from the exact
    implementation location of the analysis engine.
    """
    from analysis.engine import analyze_transactions

    return analyze_transactions


def build_analysis_result(
    analysis_id: str,
    transactions: list,
    analysis_output: dict,
) -> dict:
    """
    Combine ingestion data and Dev 1's analysis output
    into the API dashboard contract.
    """

    accounts = analysis_output["accounts"]

    graph_nodes = sorted(
        {
            transaction.source
            for transaction in transactions
        }
        |
        {
            transaction.target
            for transaction in transactions
        }
    )

    graph_edges = sorted(
        [
            {
                "id": transaction.transaction_id,
                "source": transaction.source,
                "target": transaction.target,
                "amount_minor": transaction.amount_minor,
                "timestamp": transaction.timestamp.isoformat().replace(
                    "+00:00", "Z"
                ),
            }
            for transaction in transactions
        ],
        key=lambda edge: (edge["timestamp"], edge["id"]),
    )

    alerts = []

    for account in accounts:
        if account["risk_score"] >= 40:
            alerts.append(
                {
                    "id": f"AL-{account['account_id']}",
                    "account_id": account["account_id"],
                    "status": "OPEN",
                    "updated_at": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
            )

    alerts.sort(
        key=lambda alert: (
            next(
                account["risk_score"]
                for account in accounts
                if account["account_id"] == alert["account_id"]
            ),
            alert["account_id"],
        ),
        reverse=True,
    )

    total_volume_minor = sum(
        transaction.amount_minor
        for transaction in transactions
    )

    high_risk_accounts = sum(
        account["risk_level"] in {"HIGH", "CRITICAL"}
        for account in accounts
    )

    return {
        "analysis_id": analysis_id,
        "created_at": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "engine_version": analysis_output["engine_version"],
        "currency": "INR",
        "summary": {
            "total_accounts": len(accounts),
            "total_transactions": len(transactions),
            "total_volume_minor": total_volume_minor,
            "alert_count": len(alerts),
            "high_risk_accounts": high_risk_accounts,
        },
        "accounts": accounts,
        "graph": {
            "nodes": [
                {"id": account_id}
                for account_id in graph_nodes
            ],
            "edges": graph_edges,
        },
        "alerts": alerts,
    }


def run_analysis(
    analysis_id: str,
    content: bytes,
) -> dict:
    """
    Full backend analysis pipeline:

    CSV bytes
      -> ingestion
      -> analysis engine
      -> result construction
      -> database persistence
    """

    transactions = parse_csv(content)

    analyze_transactions = get_analysis_engine()

    normalized_transactions = [
        {
            "transaction_id": transaction.transaction_id,
            "source": transaction.source,
            "target": transaction.target,
            "amount_minor": transaction.amount_minor,
            "timestamp": transaction.timestamp.isoformat().replace(
                "+00:00", "Z"
            ),
        }
        for transaction in transactions
    ]

    analysis_output = analyze_transactions(
        normalized_transactions
    )

    result = build_analysis_result(
        analysis_id=analysis_id,
        transactions=transactions,
        analysis_output=analysis_output,
    )

    save_analysis(result)

    return result