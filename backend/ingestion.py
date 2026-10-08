import csv
import io
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone

from backend.schemas import Transaction


EXPECTED_HEADERS = [
    "transaction_id",
    "source",
    "target",
    "amount",
    "timestamp",
    "currency",
]


class IngestionError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        row: int | None = None,
        field: str | None = None,
    ):
        self.code = code
        self.message = message
        self.row = row
        self.field = field

        super().__init__(message)

def validate_headers(headers: list[str]) -> None:
    if headers != EXPECTED_HEADERS:
        raise IngestionError(
            code="INVALID_CSV",
            message="CSV headers must match the required schema exactly",
            row=1,
            field=None,
        )
    

def parse_amount(value: str, row_number: int) -> int:
    value = value.strip()

    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise IngestionError(
            code="INVALID_CSV",
            message="amount must be a valid decimal number",
            row=row_number,
            field="amount",
        )

    if amount <= 0:
        raise IngestionError(
            code="INVALID_CSV",
            message="amount must be positive",
            row=row_number,
            field="amount",
        )

    if amount.as_tuple().exponent < -2:
        raise IngestionError(
            code="INVALID_CSV",
            message="amount can have at most two decimal places",
            row=row_number,
            field="amount",
        )

    amount_minor = amount * 100

    if amount_minor != amount_minor.to_integral_value():
        raise IngestionError(
            code="INVALID_CSV",
            message="amount could not be converted to paise",
            row=row_number,
            field="amount",
        )

    return int(amount_minor)  

def parse_timestamp(value: str, row_number: int) -> datetime:
    value = value.strip()

    if not value.endswith("Z"):
        raise IngestionError(
            code="INVALID_CSV",
            message="timestamp must be UTC and end with Z",
            row=row_number,
            field="timestamp",
        )

    try:
        timestamp = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        raise IngestionError(
            code="INVALID_CSV",
            message="timestamp must be a valid UTC timestamp",
            row=row_number,
            field="timestamp",
        )

    if timestamp.tzinfo is None:
        raise IngestionError(
            code="INVALID_CSV",
            message="timestamp must include UTC timezone information",
            row=row_number,
            field="timestamp",
        )

    return timestamp.astimezone(timezone.utc)


def parse_csv(content: bytes) -> list[Transaction]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise IngestionError(
            code="INVALID_CSV",
            message="CSV must be UTF-8 encoded",
        )

    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None:
        raise IngestionError(
            code="INVALID_CSV",
            message="CSV header is missing",
            row=1,
        )

    validate_headers(reader.fieldnames)

    transactions: list[Transaction] = []
    seen_ids: set[str] = set()

    for row_number, row in enumerate(reader, start=2):

        if not any(
            value is not None and value.strip()
            for value in row.values()
        ):
            continue

        transaction_id = row["transaction_id"].strip()
        source = row["source"].strip()
        target = row["target"].strip()
        currency = row["currency"].strip()

        if not transaction_id:
            raise IngestionError(
                code="INVALID_CSV",
                message="transaction_id cannot be blank",
                row=row_number,
                field="transaction_id",
            )

        if transaction_id in seen_ids:
            raise IngestionError(
                code="INVALID_CSV",
                message="duplicate transaction_id",
                row=row_number,
                field="transaction_id",
            )

        seen_ids.add(transaction_id)

        if not source:
            raise IngestionError(
                code="INVALID_CSV",
                message="source cannot be blank",
                row=row_number,
                field="source",
            )

        if not target:
            raise IngestionError(
                code="INVALID_CSV",
                message="target cannot be blank",
                row=row_number,
                field="target",
            )

        if source == target:
            raise IngestionError(
                code="INVALID_CSV",
                message="source and target must be different",
                row=row_number,
                field="target",
            )

        if currency != "INR":
            raise IngestionError(
                code="INVALID_CSV",
                message="currency must be INR",
                row=row_number,
                field="currency",
            )

        amount_minor = parse_amount(
            row["amount"],
            row_number,
        )

        timestamp = parse_timestamp(
            row["timestamp"],
            row_number,
        )

        transactions.append(
            Transaction(
                transaction_id=transaction_id,
                source=source,
                target=target,
                amount_minor=amount_minor,
                timestamp=timestamp,
            )
        )

    if not transactions:
        raise IngestionError(
            code="INVALID_CSV",
            message="CSV contains no transactions",
        )

    return transactions