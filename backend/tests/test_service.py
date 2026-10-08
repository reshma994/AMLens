import backend.service as service


def sample_engine_output():
    return {
        "engine_version": "rules-v1",
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
    }


def sample_csv():
    return (
        b"transaction_id,source,target,amount,timestamp,currency\n"
        b"T1,A,B,100000.00,2026-01-01T10:00:00Z,INR\n"
        b"T2,B,C,98000.00,2026-01-01T10:03:00Z,INR\n"
    )


def test_build_analysis_result():
    transactions = service.parse_csv(sample_csv())

    result = service.build_analysis_result(
        analysis_id="demo-001",
        transactions=transactions,
        analysis_output=sample_engine_output(),
    )

    assert result["analysis_id"] == "demo-001"
    assert result["engine_version"] == "rules-v1"
    assert result["currency"] == "INR"

    assert result["summary"]["total_accounts"] == 3
    assert result["summary"]["total_transactions"] == 2
    assert result["summary"]["total_volume_minor"] == 19800000
    assert result["summary"]["alert_count"] == 1

    assert result["graph"]["nodes"] == [
        {"id": "A"},
        {"id": "B"},
        {"id": "C"},
    ]

    assert result["graph"]["edges"][0]["id"] == "T1"
    assert result["graph"]["edges"][1]["id"] == "T2"

    assert result["alerts"][0]["id"] == "AL-B"
    assert result["alerts"][0]["status"] == "OPEN"


def test_run_analysis(monkeypatch, tmp_path):
    database_path = tmp_path / "test.db"

    monkeypatch.setattr(
        service,
        "save_analysis",
        lambda result: None,
    )

    monkeypatch.setattr(
        service,
        "get_analysis_engine",
        lambda: lambda transactions: sample_engine_output(),
    )

    result = service.run_analysis(
        analysis_id="demo-001",
        content=sample_csv(),
    )

    assert result["analysis_id"] == "demo-001"
    assert result["summary"]["total_transactions"] == 2
    assert result["summary"]["total_volume_minor"] == 19800000