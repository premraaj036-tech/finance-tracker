import typer

from .categorizer import categorize_all
from .importer import import_csv as run_import
from .models import get_session
from .reports import format_report, monthly_report

app = typer.Typer(help="Personal finance tracker.")


@app.command("import-csv")
def import_csv_command(
    path: str = typer.Argument(..., help="Path to the bank CSV file"),
    account: str = typer.Option("Default", "--account", "-a", help="Account name"),
    bank: str = typer.Option("generic", "--bank", "-b", help="Bank format: generic or hdfc"),
):
    """Import transactions from a CSV file."""
    session = get_session()
    try:
        result = run_import(session, path, account, bank)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)
    typer.echo(
        f"Imported: {result['added']} added, "
        f"{result['skipped']} duplicates skipped, {result['errors']} errors."
    )


@app.command()
def categorize():
    """Assign categories to uncategorized transactions."""
    session = get_session()
    result = categorize_all(session)
    typer.echo(f"Categorized {result['categorized']}, unmatched {result['unmatched']}.")


@app.command()
def report(month: str = typer.Argument(..., help="Month as YYYY-MM, e.g. 2026-10")):
    """Show the income and spending report for a month."""
    try:
        year_str, month_str = month.split("-")
        year, month_num = int(year_str), int(month_str)
        if not 1 <= month_num <= 12:
            raise ValueError
    except ValueError:
        typer.echo("Month must look like 2026-10", err=True)
        raise typer.Exit(code=1)

    session = get_session()
    typer.echo(format_report(monthly_report(session, year, month_num)))


if __name__ == "__main__":
    app()