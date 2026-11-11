import csv
from decimal import InvalidOperation
from pathlib import Path

from sqlalchemy.orm import Session

from .models import Account, Transaction
from .parsers import PARSERS


def get_or_create_account(session: Session, name: str) -> Account:
    account = session.query(Account).filter_by(name=name).first()
    if account is None:
        account = Account(name=name)
        session.add(account)
        session.flush()  # assigns account.id without committing
    return account


def import_csv(
    session: Session, path: str | Path, account_name: str, bank: str = "generic"
) -> dict:
    """Import a bank CSV into the given account.

    Returns counts: {"added": n, "skipped": n, "errors": n}
    """
    if bank not in PARSERS:
        raise ValueError(f"Unknown bank '{bank}'. Choose from: {', '.join(PARSERS)}")
    parse = PARSERS[bank]

    account = get_or_create_account(session, account_name)
    added = skipped = errors = 0

    with open(path, newline="", encoding="utf-8-sig") as f:
        for raw in csv.DictReader(f):
            # Bank exports often have stray spaces in the header names
            row = {(k or "").strip(): (v or "") for k, v in raw.items()}
            try:
                tx_date, description, amount = parse(row)
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
