from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .categorizer import categorize_all
from .models import Transaction, get_session
from .reports import monthly_report

app = FastAPI(title="Finance Tracker API")


def get_db():
    """Give each request its own database session, then close it."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/transactions")
def list_transactions(limit: int = 50, db: Session = Depends(get_db)):
    """Newest transactions first."""
    rows = (
        db.query(Transaction)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": t.id,
            "date": t.date.isoformat(),
            "description": t.description,
            "amount": str(t.amount),  # string keeps exact decimal precision
            "account": t.account.name,
            "category": t.category.name if t.category else None,
        }
        for t in rows
    ]


@app.post("/categorize")
def categorize(db: Session = Depends(get_db)):
    return categorize_all(db)


@app.get("/report/{year}/{month}")
def report(year: int, month: int, db: Session = Depends(get_db)):
    if not 1 <= month <= 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    result = monthly_report(db, year, month)
    return {
        "year": result["year"],
        "month": result["month"],
        "income": str(result["income"]),
        "expenses": str(result["expenses"]),
        "net": str(result["net"]),
        "by_category": {k: str(v) for k, v in result["by_category"].items()},
    }