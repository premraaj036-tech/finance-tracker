import datetime as dt
from decimal import Decimal


def _to_decimal(value: str) -> Decimal:
    """'1,299.00' -> Decimal('1299.00'); empty -> 0."""
    value = value.strip().replace(",", "")
    return Decimal(value) if value else Decimal("0")


def parse_generic(row: dict):
    """Our simple format: date,description,amount (signed)."""
    return (
        dt.date.fromisoformat(row["date"].strip()),
        row["description"].strip(),
        Decimal(row["amount"].strip()),
    )


def parse_hdfc(row: dict):
    """HDFC format: dd/mm/yy dates, separate withdrawal and deposit columns."""
    tx_date = dt.datetime.strptime(row["Date"].strip(), "%d/%m/%y").date()
    description = row["Narration"].strip()
    amount = _to_decimal(row["Deposit Amt."]) - _to_decimal(row["Withdrawal Amt."])
    return tx_date, description, amount


PARSERS = {"generic": parse_generic, "hdfc": parse_hdfc}
