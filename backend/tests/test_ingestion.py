import pytest

from backend.ingestion import IngestionError, parse_csv


VALID_CSV = """\
transaction_id,source,target,amount,timestamp,currency
T1,A,B,100000.00,2026-01-01T10:00:00Z,INR
T2,B,C,98000.00,2026-01-01T10:03:00Z,INR
"""


def test_parse_valid_csv():
    transactions = parse_csv(VALID_CSV.encode())

    assert len(transactions) == 2

    assert transactions[0].transaction_id == "T1"
    assert transactions[0].source == "A"
    assert transactions[0].target == "B"
    assert transactions[0].amount_minor == 10_000_000

    assert transactions[1].transaction_id == "T2"
    assert transactions[1].amount_minor == 9_800_000


def test_parse_utf8_bom():
    content = ("\ufeff" + VALID_CSV).encode("utf-8")

    transactions = parse_csv(content)

    assert len(transactions) == 2
    assert transactions[0].transaction_id == "T1"


def test_duplicate_transaction_id_rejected():
    csv_content = """\
transaction_id,source,target,amount,timestamp,currency
T1,A,B,100.00,2026-01-01T10:00:00Z,INR
T1,B,C,200.00,2026-01-01T10:03:00Z,INR
"""

    with pytest.raises(IngestionError) as exc:
        parse_csv(csv_content.encode())

    assert exc.value.code == "INVALID_CSV"
    assert exc.value.row == 3
    assert exc.value.field == "transaction_id"


def test_self_transfer_rejected():
    csv_content = """\
transaction_id,source,target,amount,timestamp,currency
T1,A,A,100.00,2026-01-01T10:00:00Z,INR
"""

    with pytest.raises(IngestionError) as exc:
        parse_csv(csv_content.encode())

    assert exc.value.code == "INVALID_CSV"
    assert exc.value.row == 2
    assert exc.value.field == "target"


def test_negative_amount_rejected():
    csv_content = """\
transaction_id,source,target,amount,timestamp,currency
T1,A,B,-100.00,2026-01-01T10:00:00Z,INR
"""

    with pytest.raises(IngestionError) as exc:
        parse_csv(csv_content.encode())

    assert exc.value.code == "INVALID_CSV"
    assert exc.value.row == 2
    assert exc.value.field == "amount"


def test_zero_amount_rejected():
    csv_content = """\
transaction_id,source,target,amount,timestamp,currency
T1,A,B,0.00,2026-01-01T10:00:00Z,INR
"""

    with pytest.raises(IngestionError) as exc:
        parse_csv(csv_content.encode())

    assert exc.value.code == "INVALID_CSV"
    assert exc.value.row == 2
    assert exc.value.field == "amount"


def test_more_than_two_decimal_places_rejected():
    csv_content = """\
transaction_id,source,target,amount,timestamp,currency
T1,A,B,100.001,2026-01-01T10:00:00Z,INR
"""

    with pytest.raises(IngestionError) as exc:
        parse_csv(csv_content.encode())

    assert exc.value.code == "INVALID_CSV"
    assert exc.value.row == 2
    assert exc.value.field == "amount"


def test_non_inr_currency_rejected():
    csv_content = """\
transaction_id,source,target,amount,timestamp,currency
T1,A,B,100.00,2026-01-01T10:00:00Z,USD
"""

    with pytest.raises(IngestionError) as exc:
        parse_csv(csv_content.encode())

    assert exc.value.code == "INVALID_CSV"
    assert exc.value.row == 2
    assert exc.value.field == "currency"


def test_non_utc_timestamp_rejected():
    csv_content = """\
transaction_id,source,target,amount,timestamp,currency
T1,A,B,100.00,2026-01-01T10:00:00+05:30,INR
"""

    with pytest.raises(IngestionError) as exc:
        parse_csv(csv_content.encode())

    assert exc.value.code == "INVALID_CSV"
    assert exc.value.row == 2
    assert exc.value.field == "timestamp"


def test_missing_header_rejected():
    csv_content = """\
T1,A,B,100.00,2026-01-01T10:00:00Z,INR
"""

    with pytest.raises(IngestionError) as exc:
        parse_csv(csv_content.encode())

    assert exc.value.code == "INVALID_CSV"


def test_wrong_headers_rejected():
    csv_content = """\
transaction_id,source,target,amount,timestamp
T1,A,B,100.00,2026-01-01T10:00:00Z
"""

    with pytest.raises(IngestionError) as exc:
        parse_csv(csv_content.encode())

    assert exc.value.code == "INVALID_CSV"
    assert exc.value.row == 1


def test_blank_rows_are_ignored():
    csv_content = """\
transaction_id,source,target,amount,timestamp,currency
T1,A,B,100.00,2026-01-01T10:00:00Z,INR

T2,B,C,200.00,2026-01-01T10:03:00Z,INR
"""

    transactions = parse_csv(csv_content.encode())

    assert len(transactions) == 2