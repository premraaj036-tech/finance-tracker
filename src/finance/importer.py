import csv
import datetime as dt
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy.orm import Session

from .models import Account, Transaction


def get_or_create_account(session: Session, name: str) -> Account:
    account = session.query(Account).filter_by(name=name).first()
    if account is None:
        account = Account(name=name)
        session.add(account)
        session.flush()  # assigns account.id without committing
    return account


def import_csv(session: Session, path: str | Path, account_name: str) -> dict:
    """Import a CSV (date,description,amount) into the given account.

    Returns counts: {"added": n, "skipped": n, "errors": n}
    """
    account = get_or_create_account(session, account_name)
    added = skipped = errors = 0

    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                tx_date = dt.date.fromisoformat(row["date"].strip())
                description = row["description"].strip()
                amount = Decimal(row["amount"].strip())
            except (KeyError, ValueError, InvalidOperation):
                errors += 1
                continue

            exists = (
                session.query(Transaction)
                .filter_by(
                    account_id=account.id,
                    date=tx_date,
                    description=description,
                    amount=amount,
                )
                .first()
            )
            if exists:
                skipped += 1
                continue

            session.add(
                Transaction(
                    date=tx_date,
                    description=description,
                    amount=amount,
                    account_id=account.id,
                )
            )
            added += 1

    session.commit()
    return {"added": added, "skipped": skipped, "errors": errors}