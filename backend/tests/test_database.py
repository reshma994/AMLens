import json

import backend.database as database


def sample_result():
    return {
        "analysis_id": "demo-001",
        "created_at": "2026-01-01T12:00:00Z",
        "engine_version": "rules-v1",
        "currency": "INR",
        "summary": {
            "total_accounts": 3,
            "total_transactions": 2,
            "total_volume_minor": 19800000,
            "alert_count": 1,
            "high_risk_accounts": 0,
        },
        "accounts": [
            {
                "account_id": "A",
                "risk_score": 0,
                "risk_level": "LOW",
                "reasons": [],
            },
            {
                "account_id": "B",
                "risk_score": 40,
                "risk_level": "MEDIUM",
                "reasons": [
                    {
                        "code": "RAPID_PASS_THROUGH",
                        "points": 40,
                        "transaction_ids": ["T1", "T2"],
                    }
                ],
            },
            {
                "account_id": "C",
                "risk_score": 0,
                "risk_level": "LOW",
                "reasons": [],
            },
        ],
        "graph": {
            "nodes": [
                {"id": "A"},
                {"id": "B"},
                {"id": "C"},
            ],
            "edges": [
                {
                    "id": "T1",
                    "source": "A",
                    "target": "B",
                    "amount_minor": 10000000,
                    "timestamp": "2026-01-01T10:00:00Z",
                },
                {
                    "id": "T2",
                    "source": "B",
                    "target": "C",
                    "amount_minor": 9800000,
                    "timestamp": "2026-01-01T10:03:00Z",
                },
            ],
        },
        "alerts": [
            {
                "id": "AL-B",
                "account_id": "B",
                "status": "OPEN",
                "updated_at": "2026-01-01T12:00:00Z",
            }
        ],
    }


def setup_test_db(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"

    monkeypatch.setattr(database, "DB_PATH", db_path)

    database.init_db()


def test_init_db_creates_tables(monkeypatch, tmp_path):
    setup_test_db(monkeypatch, tmp_path)

    connection = database.get_connection()

    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    ).fetchall()

    connection.close()

    table_names = {row["name"] for row in tables}

    assert "analyses" in table_names
    assert "alerts" in table_names


def test_save_and_get_analysis(monkeypatch, tmp_path):
    setup_test_db(monkeypatch, tmp_path)

    result = sample_result()

    database.save_analysis(result)

    stored = database.get_analysis("demo-001")

    assert stored is not None
    assert stored["analysis_id"] == "demo-001"
    assert stored["engine_version"] == "rules-v1"
    assert stored["summary"]["total_transactions"] == 2
    assert stored["alerts"][0]["id"] == "AL-B"
    assert stored["alerts"][0]["status"] == "OPEN"


def test_get_missing_analysis_returns_none(monkeypatch, tmp_path):
    setup_test_db(monkeypatch, tmp_path)

    result = database.get_analysis("does-not-exist")

    assert result is None


def test_update_alert_status(monkeypatch, tmp_path):
    setup_test_db(monkeypatch, tmp_path)

    database.save_analysis(sample_result())

    updated = database.update_alert_status(
        "demo-001",
        "AL-B",
        "UNDER_REVIEW",
    )

    assert updated is not None
    assert updated["status"] == "UNDER_REVIEW"

    result = database.get_analysis("demo-001")

    assert result["alerts"][0]["status"] == "UNDER_REVIEW"


def test_update_missing_alert_returns_none(monkeypatch, tmp_path):
    setup_test_db(monkeypatch, tmp_path)

    database.save_analysis(sample_result())

    result = database.update_alert_status(
        "demo-001",
        "AL-DOES-NOT-EXIST",
        "UNDER_REVIEW",
    )

    assert result is None