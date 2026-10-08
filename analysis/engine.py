import networkx as nx


def build_graph(transactions):
    graph = nx.MultiDiGraph()

    for transaction in transactions:
        graph.add_edge(
            transaction["source"],
            transaction["target"],
            key=transaction["transaction_id"],
            amount_minor=transaction["amount_minor"],
            timestamp=transaction["timestamp"]
        )

    return graph


from analysis.patterns import (
    SearchBudget,
    detect_circular_transfers,
    detect_rapid_transfers,
)


def analyze_transactions(transactions):
    graph = build_graph(transactions)
    budget = SearchBudget()

    circular = detect_circular_transfers(transactions, budget)
    rapid = detect_rapid_transfers(transactions, budget)

    accounts = []

    for account_id in sorted(graph.nodes):
        reasons = []

        if account_id in circular:
            reasons.append({
                "code": "CIRCULAR_FLOW",
                "points": 60,
                "transaction_ids": circular[account_id]
            })

        if account_id in rapid:
            reasons.append({
                "code": "RAPID_PASS_THROUGH",
                "points": 40,
                "transaction_ids": rapid[account_id]
            })

        score = min(100, sum(reason["points"] for reason in reasons))

        if score >= 80:
            level = "CRITICAL"
        elif score >= 60:
            level = "HIGH"
        elif score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"

        accounts.append({
            "account_id": account_id,
            "risk_score": score,
            "risk_level": level,
            "reasons": reasons
        })

    return {
        "engine_version": "rules-v1",
        "accounts": accounts
    }