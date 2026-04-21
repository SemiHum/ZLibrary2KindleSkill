# kindle-email

Sends a downloaded book file as an email attachment to a Kindle address via SMTP.

## Interface

**MCP tool:** `kindle_send_email`

```python
def kindle_send_email(
    file_path: str,
    book_title: str,
    recipient_email: str | None = None
) -> dict:
    """
    Returns:
        {"status": "sent", "recipient": str, "file": str}
        {"status": "error", "message": str}
    """
```

## Data Flow

```
1. path = Path(file_path); if not path.exists(): return error
2. recipient = recipient_email or KINDLE_EMAIL env var
3. Build MIMEMultipart:
   - From: SENDER_EMAIL
   - To: recipient_email
   - Subject: "[Kindle] {book_title}"
   - Body: "Your book '{book_title}' is attached."
   - Attachment: MIMEApplication(subtype=file extension)
4. SMTP:
   - SMTP(SMTP_HOST, SMTP_PORT) → starttls() → login() → sendmail()
5. path.unlink(missing_ok=True) — delete temp file after sending
6. return {"status": "sent", "recipient": recipient_email, "file": path.name}
```

## SMTP Configuration

| Env Variable | Description | Example |
|-------------|-------------|---------|
| `SENDER_EMAIL` | Gmail address | `user@gmail.com` |
| `SENDER_PASSWORD` | Gmail App Password (not login password) | `xxxx xxxx xxxx xxxx` |
| `SMTP_HOST` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |

**Gmail requires App Password, not login password.** Generate at: https://myaccount.google.com/apppasswords

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| `SMTPAuthenticationError` | Wrong password | Use App Password, not login password |
| `SMTPRecipientsRefused` | Invalid recipient email | Check Kindle email in Amazon settings |
| `File not found` | File deleted before send | Re-download the file |

## Gotchas

- **App Password required:** Gmail 2FA requires an App Password — regular password will fail with `SMTPAuthenticationError`
- **File cleanup:** File is deleted via `path.unlink(missing_ok=True)` after sending — it only exists during the send
- **Port 587 with starttls:** Standard Gmail SMTP setup; port 465 uses a different mechanism
- **Subject prefix `[Kindle]`:** Required so Amazon recognizes and delivers the email to the Kindle
- **Recipient email:** Get exact Kindle email from Amazon account settings → "Manage Your Content and Devices" → "Preferences" → "Personal Document Settings"
