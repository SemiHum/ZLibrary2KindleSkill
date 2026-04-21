# zlibrary-download

Downloads a book file from Z-Library by extracting the CDN URL and capturing the redirected download.

## Interface

**MCP tool:** `zlibrary_download`

```python
def zlibrary_download(
    book_id: str | None = None,
    download_url: str | None = None
) -> dict:
    """
    Args:
        book_id: ZLibrary book ID (preferred)
        download_url: Direct download URL fallback (e.g. "/dl/AxR7p54gzp")
    Returns:
        {"status": "success", "file_path": str, "file_name": str, "file_size": int}
        {"status": "error", "message": str}
    """
```

## Data Flow

```
Step 1 — Get download URL (using session context)
 1. new_context() with persist_session=True
 2. new_page() → navigate to https://zh.zlib.li/book/{book_id}
 3. wait_for_load_state("domcontentloaded", timeout=30s)
 4. time.sleep(3) — wait for dynamic content
 5. query_selector('a[href*="/dl/"]') → extract href
 6. ctx.close()

Step 2 — Download file (fresh context WITH session cookies)
 7. new_context() → fresh context
 8. dl_ctx.add_cookies(session_cookies) — MUST load session into fresh context
 9. new_page() → with dl_page.expect_download(timeout=60s):
10. dl_page.goto(url) — navigate to https://zh.zlib.li/dl/{id}
    (302 redirect to CDN is followed automatically; expect_download captures final file)
11. download = download_info.value
12. file_path = DOWNLOAD_DIR / download.suggested_filename
13. download.save_as(str(file_path))
14. close everything
```

## URL Construction

```python
if dl_path.startswith("http"):
    url = dl_path
elif dl_path.startswith("/"):
    url = f"{ZLIBRARY_BASE_URL}{dl_path}"
else:
    url = f"{ZLIBRARY_BASE_URL}/{dl_path}"
```

## CDN Redirect Chain

```
https://zh.zlib.li/dl/{id}
  → 302 https://dlne.ncdn.ec/books-files/.../redirection?filename=...&s=...&md5=...
  → final file download

expect_download() automatically follows the redirect chain.
```

## Verified DOM

```
Book detail page: https://zh.zlib.li/book/{book_id}/{slug}.html
a[href*="/dl/"] — download link (no login required)
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| `expect_download` timeout | CDN blocked without session cookies | Ensure `add_cookies(session_cookies)` |
| No `a[href*="/dl/"]` found | Page didn't render | Fallback: construct `/dl/{book_id}` |
| `Event loop is closed` | Called method after `pw.close()` | Don't close before getting download URL |
| `Page.goto: Download is starting` | `wait_until` specified explicitly | Use `goto(url)` with no explicit `wait_until` |

## Gotchas

- **Fresh context needs session cookies:** Without `add_cookies(session_cookies)`, CDN returns 503 — Cloudflare blocks `/dl/` navigation
- **Event loop closed:** After `pw.close()`, methods fail with "Event loop is closed". Extract download URL BEFORE closing
- **No `wait_until` in goto:** `dl_page.goto(url)` with no explicit `wait_until` avoids "Download is starting" error
- **Save before context closes:** `download.save_as()` must be called before `dl_ctx.close()`
- **Session cookies reload:** Reload from `~/.cache/zlibrary2kindle/session.json` before fresh download context
- **File cleanup:** Files in `DOWNLOAD_DIR` (`/tmp/zlibrary2kindle/downloads/`); caller deletes after emailing
