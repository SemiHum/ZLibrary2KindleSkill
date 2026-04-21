"""Kindle email sending via SMTP."""

from __future__ import annotations

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from src import config


class EmailService:
    """Sends books as email attachments to Kindle."""

    def __init__(self) -> None:
        # Resolve at construction time (creds validated at send time)
        self._host = config.get_smtp_host()
        self._port = config.get_smtp_port()
        self._sender = config.get_sender_email()
        self._password = config.get_sender_password()

    def send_book(
        self,
        file_path: Path,
        book_title: str,
        recipient_email: str,
    ) -> dict:
        """Send a book file as an attachment to a Kindle device."""
        if not file_path.exists():
            return {"status": "error", "message": f"File not found: {file_path}"}

        msg = MIMEMultipart()
        msg["From"] = self._sender
        msg["To"] = recipient_email
        msg["Subject"] = f"[Kindle] {book_title}"

        msg.attach(MIMEText(f"Your book '{book_title}' is attached.", "plain"))

        file_bytes = file_path.read_bytes()
        part = MIMEApplication(file_bytes, _subtype=file_path.suffix.lstrip("."))
        part.add_header(
            "Content-Disposition", "attachment", filename=file_path.name
        )
        msg.attach(part)

        with smtplib.SMTP(self._host, self._port) as server:
            server.starttls()
            server.login(self._sender, self._password)
            server.sendmail(self._sender, [recipient_email], msg.as_string())

        return {"status": "sent", "recipient": recipient_email, "file": file_path.name}
