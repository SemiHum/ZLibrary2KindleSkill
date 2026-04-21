## ADDED Requirements

### Requirement: CLI entry point
The system SHALL provide a `zlibrary2kindle` CLI command when installed via `pip install -e .`.

### Requirement: login subcommand
The CLI SHALL expose a `login` subcommand that authenticates to ZLibrary.

#### Scenario: Successful login
- **WHEN** user runs `zlibrary2kindle login`
- **THEN** CLI launches headless browser, submits credentials from env vars, saves session cookies, prints `"Logged in successfully"`

#### Scenario: Missing credentials
- **WHEN** user runs `zlibrary2kindle login` but `ZLIBRARY_EMAIL` or `ZLIBRARY_PASSWORD` is not set
- **THEN** CLI prints an error and exits with non-zero code

### Requirement: search subcommand
The CLI SHALL expose a `search` subcommand that searches for books.

#### Scenario: Successful search
- **WHEN** user runs `zlibrary2kindle search "随园食单"`
- **THEN** CLI prints list of matching books with title, author, book_id

#### Scenario: No results
- **WHEN** user runs `zlibrary2kindle search "nonexistent xyz"`
- **THEN** CLI prints `"No results found"` and exits with code 0

### Requirement: download subcommand
The CLI SHALL expose a `download` subcommand that downloads a book by book_id.

#### Scenario: Successful download
- **WHEN** user runs `zlibrary2kindle download <book-id>`
- **THEN** CLI downloads the book to `DOWNLOAD_DIR`, prints the file path, exits 0

#### Scenario: Download timeout
- **WHEN** user runs `zlibrary2kindle download <book-id>` but CDN does not respond
- **THEN** CLI prints an error and exits with non-zero code

### Requirement: send subcommand
The CLI SHALL expose a `send` subcommand that emails a file to Kindle.

#### Scenario: Successful send
- **WHEN** user runs `zlibrary2kindle send /path/to/book.epub "Book Title"`
- **THEN** CLI sends the file to `KINDLE_EMAIL`, prints `"Sent successfully"`, deletes the temp file

#### Scenario: File not found
- **WHEN** user runs `zlibrary2kindle send /nonexistent/file.epub "Title"`
- **THEN** CLI prints an error and exits with non-zero code

### Requirement: help output
The CLI SHALL display help when run with `--help`.

#### Scenario: Help output
- **WHEN** user runs `zlibrary2kindle --help`
- **THEN** CLI prints usage with all available subcommands
