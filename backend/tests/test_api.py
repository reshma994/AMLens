from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_rejects_non_csv():
    response = client.post(
        "/api/analyses",
        files={
            "file": (
                "transactions.txt",
                b"hello",
                "text/plain",
            )
        },
    )

    assert response.status_code == 415

    body = response.json()

    assert body["error"]["code"] == "UNSUPPORTED_FILE"


def test_get_missing_analysis():
    response = client.get(
        "/api/analyses/does-not-exist"
    )

    assert response.status_code == 404

    body = response.json()

    assert body["error"]["code"] == "NOT_FOUND"


def test_patch_missing_alert():
    response = client.patch(
        "/api/analyses/demo-001/alerts/AL-DOES-NOT-EXIST",
        json={"status": "UNDER_REVIEW"},
    )

    assert response.status_code == 404

    body = response.json()

    assert body["error"]["code"] == "NOT_FOUND"