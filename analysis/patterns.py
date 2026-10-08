from datetime import datetime


class AnalysisLimitError(Exception):
    pass


class SearchBudget:
    def __init__(self, limit=50000):
        self.limit = limit
        self.used = 0

    def consume(self):
        if self.used >= self.limit:
            raise AnalysisLimitError(
                "Dataset is too dense; upload fewer transactions"
            )
        self.used += 1


def parse_time(timestamp):
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")


def detect_rapid_transfers(transactions, budget=None):
    if budget is None:
        budget = SearchBudget()

    ordered = sorted(
        transactions,
        key=lambda t: (t["timestamp"], t["transaction_id"])
    )

    outgoing = {}
    times = {}

    for transaction in ordered:
        account = transaction["source"]
        outgoing.setdefault(account, []).append(transaction)
        times[transaction["transaction_id"]] = parse_time(
            transaction["timestamp"]
        )

    evidence = {}
    best_keys = {}

    for incoming in ordered:
        middle = incoming["target"]
        start = times[incoming["transaction_id"]]

        for outgoing_transaction in outgoing.get(middle, []):
            budget.consume()

            end = times[outgoing_transaction["transaction_id"]]
            seconds = (end - start).total_seconds()

            if seconds <= 0:
                continue

            if seconds > 300:
                break

            accounts = {
                incoming["source"],
                middle,
                outgoing_transaction["target"]
            }

            if len(accounts) != 3:
                continue

            incoming_amount = incoming["amount_minor"]
            outgoing_amount = outgoing_transaction["amount_minor"]

            # Integer arithmetic avoids floating-point rounding.
            if not (
                80 * incoming_amount
                <= 100 * outgoing_amount
                <= 120 * incoming_amount
            ):
                continue

            transaction_ids = [
                incoming["transaction_id"],
                outgoing_transaction["transaction_id"]
            ]

            candidate_key = (start, end, tuple(transaction_ids))

            if middle not in best_keys or candidate_key < best_keys[middle]:
                best_keys[middle] = candidate_key
                evidence[middle] = transaction_ids

    return evidence

def detect_circular_transfers(transactions, budget=None):
    if budget is None:
        budget = SearchBudget()

    ordered = sorted(
        transactions,
        key=lambda t: (t["timestamp"], t["transaction_id"])
    )

    outgoing = {}
    times = {}

    for transaction in ordered:
        outgoing.setdefault(transaction["source"], []).append(transaction)
        times[transaction["transaction_id"]] = parse_time(
            transaction["timestamp"]
        )

    evidence = {}
    best_keys = {}

    def search(path, visited):
        first = path[0]
        last = path[-1]

        if len(path) >= 4:
            return

        for transaction in outgoing.get(last["target"], []):
            budget.consume()

            end = times[transaction["transaction_id"]]
            start = times[first["transaction_id"]]
            previous = times[last["transaction_id"]]

            if end <= previous:
                continue

            if (end - start).total_seconds() > 3600:
                break

            if not (
                80 * first["amount_minor"]
                <= 100 * transaction["amount_minor"]
                <= 120 * first["amount_minor"]
            ):
                continue

            new_path = path + [transaction]
            target = transaction["target"]

            if target == first["source"]:
                if len(new_path) not in (3, 4):
                    continue

                ids = [t["transaction_id"] for t in new_path]
                candidate_key = (start, end, tuple(ids))

                for account in visited:
                    if (
                        account not in best_keys
                        or candidate_key < best_keys[account]
                    ):
                        best_keys[account] = candidate_key
                        evidence[account] = ids

            elif target not in visited:
                search(new_path, visited | {target})

    for transaction in ordered:
        search(
            [transaction],
            {transaction["source"], transaction["target"]}
        )

    return evidence