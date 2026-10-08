import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "runtime" / "amlens.db"


class DatabaseError(Exception):
    pass


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db() -> None:
    connection = get_connection()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                analysis_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                engine_version TEXT NOT NULL,
                currency TEXT NOT NULL,
                total_accounts INTEGER NOT NULL,
                total_transactions INTEGER NOT NULL,
                total_volume_minor INTEGER NOT NULL,
                alert_count INTEGER NOT NULL,
                high_risk_accounts INTEGER NOT NULL,
                result_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                account_id TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                FOREIGN KEY (analysis_id)
                    REFERENCES analyses(analysis_id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_alerts_analysis_id
                ON alerts(analysis_id);

            CREATE INDEX IF NOT EXISTS idx_alerts_status
                ON alerts(status);
            """
        )

        connection.commit()

    except sqlite3.Error as exc:
        connection.rollback()
        raise DatabaseError("Failed to initialize database") from exc

    finally:
        connection.close()


def save_analysis(result: dict) -> None:
    connection = get_connection()

    try:
        summary = result["summary"]

        connection.execute(
            """
            INSERT INTO analyses (
                analysis_id,
                created_at,
                engine_version,
                currency,
                total_accounts,
                total_transactions,
                total_volume_minor,
                alert_count,
                high_risk_accounts,
                result_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result["analysis_id"],
                result["created_at"],
                result["engine_version"],
                result["currency"],
                summary["total_accounts"],
                summary["total_transactions"],
                summary["total_volume_minor"],
                summary["alert_count"],
                summary["high_risk_accounts"],
                json.dumps(result),
            ),
        )

        for alert in result["alerts"]:
            account = next(
                account
                for account in result["accounts"]
                if account["account_id"] == alert["account_id"]
            )

            connection.execute(
                """
                INSERT INTO alerts (
                    alert_id,
                    analysis_id,
                    account_id,
                    risk_score,
                    risk_level,
                    status,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert["id"],
                    result["analysis_id"],
                    alert["account_id"],
                    account["risk_score"],
                    account["risk_level"],
                    alert["status"],
                    alert["updated_at"],
                ),
            )

        connection.commit()

    except (sqlite3.Error, KeyError, StopIteration) as exc:
        connection.rollback()
        raise DatabaseError("Failed to save analysis") from exc

    finally:
        connection.close()


def get_analysis(analysis_id: str) -> dict | None:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT result_json
            FROM analyses
            WHERE analysis_id = ?
            """,
            (analysis_id,),
        ).fetchone()

        if row is None:
            return None

        result = json.loads(row["result_json"])

        alert_rows = connection.execute(
            """
            SELECT alert_id, status, updated_at
            FROM alerts
            WHERE analysis_id = ?
            """,
            (analysis_id,),
        ).fetchall()

        alert_map = {
            row["alert_id"]: {
                "status": row["status"],
                "updated_at": row["updated_at"],
            }
            for row in alert_rows
        }

        for alert in result["alerts"]:
            stored = alert_map.get(alert["id"])

            if stored:
                alert["status"] = stored["status"]
                alert["updated_at"] = stored["updated_at"]

        return result

    except (sqlite3.Error, json.JSONDecodeError, KeyError) as exc:
        raise DatabaseError("Failed to retrieve analysis") from exc

    finally:
        connection.close()


def update_alert_status(
    analysis_id: str,
    alert_id: str,
    status: str,
) -> dict | None:
    connection = get_connection()

    try:
        updated_at = (
            datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

        cursor = connection.execute(
            """
            UPDATE alerts
            SET status = ?, updated_at = ?
            WHERE alert_id = ?
              AND analysis_id = ?
            """,
            (
                status,
                updated_at,
                alert_id,
                analysis_id,
            ),
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return None

        connection.commit()

        return {
            "status": status,
            "updated_at": updated_at,
        }

    except sqlite3.Error as exc:
        connection.rollback()
        raise DatabaseError("Failed to update alert") from exc

    finally:
        connection.close()