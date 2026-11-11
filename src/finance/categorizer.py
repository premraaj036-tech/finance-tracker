from sqlalchemy.orm import Session

from .models import Category, Transaction

# keyword (lowercase) -> category name. Add your own as you go.
DEFAULT_RULES = {
    "salary": "Income",
    "swiggy": "Food",
    "zomato": "Food",
    "uber": "Transport",
    "ola": "Transport",
    "amazon": "Shopping",
    "flipkart": "Shopping",
    "electricity": "Bills",
    "recharge": "Bills",
    "netflix": "Entertainment",
}


def get_or_create_category(session: Session, name: str) -> Category:
    category = session.query(Category).filter_by(name=name).first()
    if category is None:
        category = Category(name=name)
        session.add(category)
        session.flush()
    return category


def categorize_description(description: str, rules: dict[str, str]) -> str | None:
    """Return the category name for a description, or None if nothing matches."""
    text = description.lower()
    for keyword, category_name in rules.items():
        if keyword in text:
            return category_name
    return None


def categorize_all(session: Session, rules: dict[str, str] | None = None) -> dict:
    """Assign categories to all uncategorized transactions."""
    rules = rules or DEFAULT_RULES
    categorized = unmatched = 0

    uncategorized = session.query(Transaction).filter(Transaction.category_id.is_(None)).all()
    for tx in uncategorized:
        name = categorize_description(tx.description, rules)
        if name is None:
            unmatched += 1
            continue
        tx.category = get_or_create_category(session, name)
        categorized += 1

    session.commit()
    return {"categorized": categorized, "unmatched": unmatched}