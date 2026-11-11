import pytest

from src.finance.models import get_session


@pytest.fixture
def session():
    """A fresh, empty in-memory database for each test."""
    s = get_session("sqlite:///:memory:")
    yield s
    s.close()


@pytest.fixture
def sample_csv(tmp_path):
    """A small CSV written to a temp folder."""
    path = tmp_path / "bank.csv"
    path.write_text(
        "date,description,amount\n"
        "2026-10-01,SALARY ACME CORP,75000\n"
        "2026-10-02,SWIGGY ORDER 8821,-450\n"
        "2026-10-03,UBER TRIP,-230\n"
        "2026-10-05,AMAZON PURCHASE,-1299\n"
        "2026-10-07,ELECTRICITY BILL,-1800\n"
    )
    return path
