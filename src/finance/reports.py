import calendar
import datetime as dt
from collections import defaultdict
from decimal import Decimal

from sqlalchemy.orm import Session

from .models import Transaction


def monthly_report(session: Session, year: int, month: int) -> dict:
    """Summarize income, expenses and spending by category for one month."""
    start = dt.date(year, month, 1)
    end = dt.date(year, month, calendar.monthrange(year, month)[1])

    transactions = (
        session.query(Transaction)
        .filter(Transaction.date >= start, Transaction.date <= end)
        .all()
    )

    income = Decimal("0")
    expenses = Decimal("0")
    by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for tx in transactions:
        if tx.amount > 0:
            income += tx.amount
        else:
            spent = -tx.amount
            expenses += spent
            name = tx.category.name if tx.category else "Uncategorized"
            by_category[name] += spent

    # Biggest spending category first
    sorted_categories = dict(
        sorted(by_category.items(), key=lambda item: item[1], reverse=True)
    )

    return {
        "year": year,
        "month": month,
        "income": income,
        "expenses": expenses,
        "net": income - expenses,
        "by_category": sorted_categories,
    }


def format_report(report: dict) -> str:
    """Turn a report dict into readable text for the terminal."""
    lines = [
        f"Report for {report['year']}-{report['month']:02d}",
        f"Income:   {report['income']:>12,.2f}",
        f"Expenses: {report['expenses']:>12,.2f}",
        f"Net:      {report['net']:>12,.2f}",
        "",
        "Spending by category:",
    ]
    total = report["expenses"]
    for name, amount in report["by_category"].items():
        pct = (amount / total * 100) if total else Decimal("0")
        lines.append(f"  {name:<15}{amount:>12,.2f}  ({pct:.1f}%)")
    return "\n".join(lines)