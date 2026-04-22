# ZLibrary2Kindle — Beginner Guide

Even if you know nothing about programming, just follow these steps and you'll have books on your Kindle.

---

## Step 1: One-Time Setup

### 1.1 What You Need

- A ZLibrary account (free: https://zh.zlib.li/ )
- A Kindle (US/JP/HK) or Kindle App
- A Gmail account (to send emails to Kindle)

### 1.2 Allow Gmail on Your Kindle

> Do this once, it lasts forever.

1. Go to Amazon.com, sign in
2. Go to "Manage Content and Devices" → "Preferences"
3. Find "Approved Personal Document E-mail List", add your Gmail address
4. Note your Kindle email (format: `yourname@kindle.com`)

### 1.3 Get a Gmail App Password

> Required if your Gmail has 2-step verification enabled.

1. Gmail → Settings → See all settings → Accounts
2. Security → App passwords → Create
3. Select "Mail" and "Mac", generate a 16-character password
4. Copy it — you'll need it in a moment

### 1.4 Install Python (if it says "python not found")

Mac has Python pre-installed, but install Homebrew and Python to be safe:

```bash
# Open Terminal, run:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew install python
```

### 1.5 Install the Software

Open Terminal and run:

```bash
# No install needed — run directly with uvx
uvx zlibrary2kindle login
```

---

## Step 2: One-Time Configuration

### 2.1 Configure Environment Variables

Open Terminal and run:

```bash
# Edit ~/.zshrc
nano ~/.zshrc
```

Press `Ctrl+V` to jump to the bottom, paste this (replace emails/passwords with your own):

```bash
export ZLIBRARY_EMAIL="your@email.com"
export ZLIBRARY_PASSWORD="your-password"
export KINDLE_EMAIL="your-name@kindle.com"
export SENDER_EMAIL="your@email.com"
export SENDER_PASSWORD="xxxx xxxx xxxx xxxx"
```

Press `Ctrl+O` to save, `Ctrl+X` to exit.

Then run:
```bash
source ~/.zshrc
```

### 2.2 Verify Configuration

Run:
```bash
uvx zlibrary2kindle login
```

If you see "Logged in successfully" — you're ready!

---

## Step 3: Find, Download, Send (repeat every time)

### 3.1 Search for Books

```bash
uvx zlibrary2kindle search "book title or author"
```

Example — search for "Harry Potter":
```bash
uvx zlibrary2kindle search "Harry Potter"
```

You'll see results like:
```
[abc123XYZ] Harry Potter and the Sorcerer's Stone | J.K. Rowling
[def456UVW] Harry Potter Collection | J.K. Rowling
```

The text in brackets `[abc123XYZ]` is the book ID. Copy it.

### 3.2 Download the Book

```bash
uvx zlibrary2kindle download 刚才复制的ID
```

Example:
```bash
uvx zlibrary2kindle download abc123XYZ
```

When done, you'll see the saved path:
```
Downloaded: /tmp/zlibrary2kindle/downloads/Harry Potter.epub
```

### 3.3 Send to Kindle

```bash
uvx zlibrary2kindle send 下载路径 "书名"
```

Example:
```bash
uvx zlibrary2kindle send "/tmp/zlibrary2kindle/downloads/Harry Potter.epub" "Harry Potter"
```

If you see "Sent successfully" — the book will appear on your Kindle in a few minutes!

---

## FAQ

### Q: Says "command not found: python"
A: Try `python3` instead of `python`

### Q: Says "No module named src"
A: Make sure you're in the project directory, or use `python -m src.cli`

### Q: Download fails with timeout
A: ZLibrary might be down. Wait a few minutes and try again. Or try non-headless mode:
```bash
uvx zlibrary2kindle login --no-headless
```

### Q: Email fails with "file too large"
A: PDFs are usually too big. Try finding an EPUB version, or search for "book title epub"

### Q: Chinese characters look wrong on Kindle
A: EPUB format renders Chinese much better. Try to download EPUB version when available.

### Q: Do I need to login every time?
A: No! After the first login, your session is saved automatically. Just search and download.
