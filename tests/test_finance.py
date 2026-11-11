from decimal import Decimal

from src.finance.categorizer import categorize_all, categorize_description
from src.finance.importer import import_csv
from src.finance.models import Transaction
from src.finance.reports import monthly_report


# ---------- importer ----------

def test_import_adds_all_rows(session, sample_csv):
    result = import_csv(session, sample_csv, "HDFC Savings")
    assert result == {"added": 5, "skipped": 0, "errors": 0}
    assert session.query(Transaction).count() == 5


def test_import_twice_skips_duplicates(session, sample_csv):
    import_csv(session, sample_csv, "HDFC Savings")
    result = import_csv(session, sample_csv, "HDFC Savings")
    assert result == {"added": 0, "skipped": 5, "errors": 0}
    assert session.query(Transaction).count() == 5


def test_import_counts_bad_rows_as_errors(session, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "date,description,amount\n"
        "not-a-date,TEST,100\n"
        "2026-10-01,GOOD ROW,-50\n"
        "2026-10-02,BAD AMOUNT,abc\n"
    )
    result = import_csv(session, bad, "Test")
    assert result == {"added": 1, "skipped": 0, "errors": 2}


def test_amounts_are_exact_decimals(session, tmp_path):
    f = tmp_path / "pennies.csv"
    f.write_text("date,description,amount\n2026-10-01,TEST,0.10\n2026-10-01,TEST2,0.20\n")
    import_csv(session, f, "Test")
    total = sum(t.amount for t in session.query(Transaction).all())
    assert total == Decimal("0.30")  # would fail with floats


# ---------- categorizer ----------

def test_categorize_description_matches_keyword():
    rules = {"swiggy": "Food"}
    assert categorize_description("SWIGGY ORDER 123", rules) == "Food"


def test_categorize_description_no_match():
    assert categorize_description("RANDOM SHOP", {"swiggy": "Food"}) is None


def test_categorize_all_assigns_categories(session, sample_csv):
    import_csv(session, sample_csv, "HDFC Savings")
    result = categorize_all(session)
    assert result == {"categorized": 5, "unmatched": 0}
    uber = session.query(Transaction).filter_by(description="UBER TRIP").one()
    assert uber.category.name == "Transport"


def test_categorize_all_leaves_unknown_uncategorized(session, tmp_path):
    f = tmp_path / "x.csv"
    f.write_text("date,description,amount\n2026-10-01,MYSTERY SHOP,-100\n")
    import_csv(session, f, "Test")
    result = categorize_all(session)
    assert result == {"categorized": 0, "unmatched": 1}


# ---------- reports ----------

def test_monthly_report_totals(session, sample_csv):
    import_csv(session, sample_csv, "HDFC Savings")
    categorize_all(session)
    report = monthly_report(session, 2026, 10)
    assert report["income"] == Decimal("75000")
    assert report["expenses"] == Decimal("3779")
    assert report["net"] == Decimal("71221")


def test_monthly_report_sorted_by_spend(session, sample_csv):
    import_csv(session, sample_csv, "HDFC Savings")
    categorize_all(session)
    report = monthly_report(session, 2026, 10)
    assert list(report["by_category"])[0] == "Bills"  # biggest spend first


def test_monthly_report_empty_month(session):
    report = monthly_report(session, 2026, 2)
    assert report["income"] == Decimal("0")
    assert report["by_category"] == {}
