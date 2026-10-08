import pytest

from analysis.patterns import detect_rapid_transfers


@pytest.mark.parametrize(
    "timestamp, amount, target, should_flag",
    [
        ("2026-01-01T10:03:00Z", 98000, "C", True),
        ("2026-01-01T10:05:00Z", 80000, "C", True),
        ("2026-01-01T10:05:00Z", 120000, "C", True),
        ("2026-01-01T10:05:01Z", 98000, "C", False),
        ("2026-01-01T10:00:00Z", 98000, "C", False),
        ("2026-01-01T09:59:00Z", 98000, "C", False),
        ("2026-01-01T10:03:00Z", 79999, "C", False),
        ("2026-01-01T10:03:00Z", 120001, "C", False),
        ("2026-01-01T10:03:00Z", 98000, "A", False),
    ]
)
def test_rapid_transfer_rules(timestamp, amount, target, should_flag):
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
            "source": "B",
            "target": target,
            "amount_minor": amount,
            "timestamp": timestamp
        }
    ]

    result = detect_rapid_transfers(transactions)

    expected = {"B": ["T1", "T2"]} if should_flag else {}
    assert result == expected


from analysis.patterns import detect_circular_transfers


@pytest.mark.parametrize(
    "last_time, last_amount, should_flag",
    [
        ("2026-01-01T10:04:00Z", 95000, True),
        ("2026-01-01T11:00:00Z", 80000, True),
        ("2026-01-01T11:00:01Z", 95000, False),
        ("2026-01-01T10:02:00Z", 95000, False),
        ("2026-01-01T10:04:00Z", 79999, False),
    ]
)
def test_circular_transfer_rules(last_time, last_amount, should_flag):
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
            "source": "B",
            "target": "C",
            "amount_minor": 98000,
            "timestamp": "2026-01-01T10:02:00Z"
        },
        {
            "transaction_id": "T3",
            "source": "C",
            "target": "A",
            "amount_minor": last_amount,
            "timestamp": last_time
        }
    ]

    result = detect_circular_transfers(transactions)

    expected = (
        {account: ["T1", "T2", "T3"] for account in ["A", "B", "C"]}
        if should_flag else {}
    )

    assert result == expected