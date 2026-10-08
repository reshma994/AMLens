from analysis.engine import build_graph


def test_build_graph_preserves_repeated_transfers():
    transactions = [
        {
            "transaction_id": "T1",
            "source": "A",
            "target": "B",
            "amount_minor": 100000,
            "timestamp": "2026-01-01T10:00:00Z"
        },
        {
            "transaction_id": "T2",
            "source": "A",
            "target": "B",
            "amount_minor": 200000,
            "timestamp": "2026-01-01T11:00:00Z"
        }
    ]

    graph = build_graph(transactions)

    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 2

    assert graph.has_edge("A", "B", key="T1")
    assert graph.has_edge("A", "B", key="T2")
    assert not graph.has_edge("B", "A")

    assert graph["A"]["B"]["T1"]["amount_minor"] == 100000
    assert graph["A"]["B"]["T2"]["amount_minor"] == 200000

import csv
from decimal import Decimal
from pathlib import Path

from analysis.engine import analyze_transactions


def test_demo_analysis():
    csv_path = Path(__file__).resolve().parents[2] / "data" / "demo.csv"

    transactions = []

    with csv_path.open(newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            transactions.append({
                "transaction_id": row["transaction_id"],
                "source": row["source"],
                "target": row["target"],
                "amount_minor": int(Decimal(row["amount"]) * 100),
                "timestamp": row["timestamp"]
            })

    result = analyze_transactions(transactions)

    assert result["engine_version"] == "rules-v1"
    assert len(transactions) == 17
    assert len(result["accounts"]) == 22

    accounts = {
        account["account_id"]: account
        for account in result["accounts"]
    }

    flagged_scores = {
        account_id: account["risk_score"]
        for account_id, account in accounts.items()
        if account["risk_score"] > 0
    }

    assert flagged_scores == {
        "A": 60,
        "B": 100,
        "C": 100,
        "D": 100,
        "R2": 40,
        "S2": 40
    }

    assert accounts["A"]["risk_level"] == "HIGH"
    assert accounts["B"]["risk_level"] == "CRITICAL"
    assert accounts["R2"]["risk_level"] == "MEDIUM"
    assert accounts["N01"]["risk_level"] == "LOW"

    assert accounts["B"]["reasons"] == [
        {
            "code": "CIRCULAR_FLOW",
            "points": 60,
            "transaction_ids": ["C01", "C02", "C03", "C04"]
        },
        {
            "code": "RAPID_PASS_THROUGH",
            "points": 40,
            "transaction_ids": ["C01", "C02"]
        }
    ]