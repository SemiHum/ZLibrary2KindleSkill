"""CLI entry point for zlibrary2kindle."""

from __future__ import annotations

import json
from pathlib import Path

import click

from src import config
from src.services.email_service import EmailService
from src.services.playwright_service import PlaywrightService
from src.services.zlibrary_service import ZLibraryService


@click.group()
def main() -> None:
    """ZLibrary2Kindle — search books, download, and send to your Kindle."""
    pass


@main.command()
@click.option("--headless/--no-headless", default=True, help="Run browser headless")
def login(headless: bool) -> None:
    """Authenticate to ZLibrary."""
    try:
        email = config.get_zlibrary_email()
        password = config.get_zlibrary_password()
    except EnvironmentError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.exit(1)

    pw = PlaywrightService()
    pw.launch(headless=headless)
    pw.new_context()
    zlib = ZLibraryService(pw)

    try:
        result = zlib.login(email, password)
        if result.get("status") == "logged_in":
            click.echo("Logged in successfully")
        else:
            click.echo(f"Login failed: {result}", err=True)
            raise click.exit(1)
    finally:
        pw.close()


@main.command()
@click.argument("query")
@click.option("--limit", default=10, help="Maximum number of results")
def search(query: str, limit: int) -> None:
    """Search for books on ZLibrary."""
    pw = PlaywrightService()
    pw.launch()
    pw.new_context()
    zlib = ZLibraryService(pw)

    try:
        results = zlib.search(query, limit=limit)
        if not results:
            click.echo("No results found")
            return
        for r in results:
            click.echo(f"[{r.book_id}] {r.title} | {r.author}")
    finally:
        pw.close()


@main.command()
@click.argument("book_id")
def download(book_id: str) -> None:
    """Download a book by its ZLibrary book ID."""
    pw = PlaywrightService()
    pw.launch()
    ctx = pw.new_context()
    zlib = ZLibraryService(pw)

    try:
        dl_path = zlib.get_download_url(book_id)
    finally:
        ctx.close()

    if not dl_path:
        click.echo(f"Could not find download link for {book_id}", err=True)
        raise click.exit(1)

    if config.ZLIBRARY_SESSION_PATH.exists():
        session_cookies = json.loads(config.ZLIBRARY_SESSION_PATH.read_text())
    else:
        session_cookies = []

    dl_ctx = pw.new_context()
    dl_ctx.add_cookies(session_cookies)
    dl_page = dl_ctx.new_page()

    if dl_path.startswith("http"):
        url = dl_path
    elif dl_path.startswith("/"):
        url = f"{config.ZLIBRARY_BASE_URL}{dl_path}"
    else:
        url = f"{config.ZLIBRARY_BASE_URL}/{dl_path}"

    try:
        with dl_page.expect_download(timeout=60_000) as download_info:
            dl_page.goto(url)
        download = download_info.value
        file_path = config.DOWNLOAD_DIR / download.suggested_filename
        download.save_as(str(file_path))
        click.echo(f"Downloaded: {file_path}")
    finally:
        dl_ctx.close()
        pw.close()


@main.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.argument("book_title")
@click.option("--to", "recipient", default=None, help="Kindle email address")
def send(file_path: Path, book_title: str, recipient: str | None) -> None:
    """Send a book file to your Kindle."""
    if recipient is None:
        try:
            recipient = config.get_kindle_email()
        except EnvironmentError as e:
            click.echo(f"Error: {e}", err=True)
            raise click.exit(1)

    email_svc = EmailService()
    result = email_svc.send_book(file_path, book_title, recipient)

    if result.get("status") == "sent":
        click.echo(f"Sent successfully to {recipient}")
    else:
        click.echo(f"Send failed: {result.get('message', result)}", err=True)
        raise click.exit(1)


if __name__ == "__main__":
    main()
