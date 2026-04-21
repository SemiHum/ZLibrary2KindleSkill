# zlibrary-search

Searches Z-Library for books and returns structured metadata.

## Interface

**MCP tool:** `zlibrary_search`

```python
def zlibrary_search(
    query: str,
    limit: int = 10,
    offset: int = 0
) -> dict:
    """
    Returns:
        {
            "status": "success",
            "query": str,
            "count": int,
            "books": [
                {
                    "title": str,
                    "author": str,
                    "year": str,       # always "" (not extracted)
                    "format": str,     # always "" (not extracted)
                    "size": str,       # always "" (not extracted)
                    "download_url": str,  # e.g. "/book/w8n2rz2N8Q/..."
                    "book_id": str     # e.g. "w8n2rz2N8Q"
                }
            ]
        }
        {"status": "error", "message": str}
    """
```

## Data Flow

```
1. Load session cookies via new_context(persist_session=True)
2. new_page() → navigate to https://zh.zlib.li/s/{query}
3. wait_for_load_state("domcontentloaded", timeout=30s)
4. wait_for_selector("z-cover", timeout=10s) — wait for JS rendering
5. query_selector_all("a[href*='/book/'][href*='.html']") — find book cards
6. For each card:
   a. Extract book_id from URL: /book/{book_id}/{slug}.html
   b. Extract title from: z-cover.getAttribute("title")
   c. Extract author from: z-cover.getAttribute("authors").split(",")[0]
   d. Fallback author: recursive text search for last line before "已下载"
7. Deduplicate by book_id, apply offset/limit
8. close browser
```

## Verified DOM

```
Search results page: https://zh.zlib.li/s/{query}
├── <z-cover> — custom element (Shadow DOM)
│   ├── @title — book title (string attribute)
│   └── @authors — comma-separated authors (string attribute)
└── <a href="/book/{book_id}/{slug}.html"> — book card link

Note: z-cover.inner_text() returns empty — title/author come from attributes only.
Author fallback: inner_text of nested elements, last line before "已下载" marker.
```

## BookMetadata Dataclass

```python
@dataclass
class BookMetadata:
    title: str       # from z-cover@title
    author: str      # from z-cover@authors or nested text before "已下载"
    year: str        # always "" — not extracted
    language: str    # always "" — not extracted
    format: str      # always "" — not extracted
    size: str        # always "" — not extracted
    download_url: str  # e.g. "/book/w8n2rz2N8Q/随园食单.html"
    book_id: str     # e.g. "w8n2rz2N8Q"
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Timeout on search page | Network issue, IP blocked | Retry, check session cookies |
| 0 results returned | Query has no matches, or JS didn't render | Try simpler query |
| Shadow DOM title empty | Site DOM changed | Update selector in zlibrary_service.py |

## Gotchas

- **Shadow DOM:** `z-cover` elements use Shadow DOM — inner_text is always empty; read `title` and `authors` attributes
- **Title from attribute:** `cover.get_attribute("title")` is the correct way to get the book title, not `inner_text()`
- **Author fallback:** Some books don't have `authors` attribute on `z-cover`. Extract from nested text by finding the last line before "已下载" in the card
- **Deduplication required:** Same book_id appears multiple times per card (cover link + title link + author link). Deduplicate before returning
- **Limit/offset applied after dedup:** `offset` and `limit` slicing happens on the deduplicated list
- **Non-logged-in search:** Works without login but results may be limited (2600/day unauthenticated)
