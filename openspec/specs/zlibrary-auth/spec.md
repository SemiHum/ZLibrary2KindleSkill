# zlibrary-auth

Establishes and persists an authenticated ZLibrary session using Playwright.

## Interface

**MCP tool:** `zlibrary_login`

```python
def zlibrary_login(headless: bool = True) -> dict:
    """
    Args:
        headless: Run browser in headless mode. Set False for debugging.
    Returns:
        {"status": "logged_in", "url": str}  # url after redirect
        {"status": "error", "message": str}
    """
```

**Environment variables required:**
- `ZLIBRARY_EMAIL` — ZLibrary account email
- `ZLIBRARY_PASSWORD` — ZLibrary account password

## Data Flow

```
1. Launch Playwright Chromium (headless=True by default)
2. new_context() — creates browser context with realistic headers
   - User-Agent: Chrome 121 on macOS
   - Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7
   - Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,...
3. new_page() → navigate to https://zh.zlib.li/login
4. fill("input[name='email']", email)
5. fill("input[name='password']", password)
6. click("button:has-text('登录')")
7. wait_for_url(lambda url: "login" not in url) — wait for redirect away from /login
8. save_session() — write cookies to ~/.cache/zlibrary2kindle/session.json
9. close browser
```

## Session Persistence

- **Path:** `~/.cache/zlibrary2kindle/session.json` (configurable via `ZLIBRARY_SESSION_PATH`)
- **Format:** JSON array of Playwright cookie dicts
  ```json
  [
    {"name": "bsrv", "value": "REDACTED", "domain": "zh.zlib.li", "path": "/"},
    {"name": "c_token", "value": "REDACTED", "domain": "zh.zlib.li", "path": "/"},
    {"name": "remix_userkey", "value": "REDACTED", "domain": ".zlib.li", "path": "/"},
    {"name": "siteLanguage", "value": "REDACTED", "domain": ".zlib.li", "path": "/"}
  ]
  ```
- **Domain scope:** Some cookies use `.zlib.li` (all subdomains), others use `zh.zlib.li` (specific subdomain)
- **Reuse:** `new_context(persist_session=True)` loads cookies automatically on startup
- **Expiry:** Session cookies typically valid for ~30 days; expired cookies cause redirects to `/login`

## Verified DOM

```
Login page: https://zh.zlib.li/login
├── input[name="email"]
├── input[name="password"]
└── button:has-text("登录")
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Timeout waiting for redirect | Wrong credentials, network issue | Retry with correct creds |
| 403 on login page | IP blocked / rate limited | Wait, use VPN, or manual cookie export |
| `wait_for_url` timeout | Login form selector changed | Update DOM selectors in zlibrary_service.py |

## Gotchas

- **Do not call `pw.close()` before `save_session()`** — cookies won't persist
- **Login redirect check:** Use `wait_for_url(lambda url: "login" not in url)` — glob patterns like `!**/login**` do not work reliably with redirects
- **Session cookies from different subdomain:** Cookies from `.zlib.li` and `zh.zlib.li` must both be loaded for full site access
- **Cloudflare:** May present CAPTCHA or temporary block; if persistent, export cookies manually from browser
