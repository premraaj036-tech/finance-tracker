from decimal import Decimal
from pathlib import Path

import pytest

from src.finance.importer import import_csv
from src.finance.models import Transaction

HDFC_SAMPLE = Path(__file__).parent.parent / "data" / "hdfc_sample.csv"


def test_hdfc_import_adds_all_rows(session):
    result = import_csv(session, HDFC_SAMPLE, "HDFC Savings", bank="hdfc")
    assert result == {"added": 7, "skipped": 0, "errors": 0}


def test_hdfc_withdrawals_are_negative_and_deposits_positive(session):
    import_csv(session, HDFC_SAMPLE, "HDFC Savings", bank="hdfc")
    salary = session.query(Transaction).filter(Transaction.description.like("%SALARY%")).one()
    swiggy = session.query(Transaction).filter(Transaction.description.like("%SWIGGY%")).one()
    assert salary.amount == Decimal("75000.00")
    assert swiggy.amount == Decimal("-450.00")


def test_hdfc_amounts_with_commas(session):
    import_csv(session, HDFC_SAMPLE, "HDFC Savings", bank="hdfc")
    atm = session.query(Transaction).filter(Transaction.description.like("ATM%")).one()
    assert atm.amount == Decimal("-5000.00")


def test_hdfc_dates_parse_day_first(session):
    import_csv(session, HDFC_SAMPLE, "HDFC Savings", bank="hdfc")
    first = session.query(Transaction).order_by(Transaction.date).first()
    assert (first.date.year, first.date.month, first.date.day) == (2026, 10, 1)


def test_hdfc_reimport_skips_duplicates(session):
    import_csv(session, HDFC_SAMPLE, "HDFC Savings", bank="hdfc")
    result = import_csv(session, HDFC_SAMPLE, "HDFC Savings", bank="hdfc")
    assert result == {"added": 0, "skipped": 7, "errors": 0}


def test_unknown_bank_raises(session):
    with pytest.raises(ValueError):
        import_csv(session, HDFC_SAMPLE, "X", bank="nonexistent")
