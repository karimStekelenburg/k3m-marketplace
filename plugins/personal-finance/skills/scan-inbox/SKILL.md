---
name: scan-inbox
description: Use when the user wants to scan Apple Mail for invoice emails, find invoice-related messages, check for new invoices, or search their mailbox for bills and payment requests.
version: 0.1.0
argument-hint: "[--days 90] [--data-dir PATH]"
allowed-tools: Bash
---

Parse arguments from $ARGUMENTS. Determine the data directory: use the value passed via `--data-dir` if provided, otherwise default to `~/Documents/finance-data/`.

Build the command arguments from whatever options the user supplied:
- `--days N` controls how far back to search (default: 90 days if not specified)
- `--data-dir PATH` passes the resolved data directory

Run the inbox scanner:

```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/scan_inbox.py [--days N] [--data-dir PATH]
```

Wait for the script to complete. Parse its output to extract:
- Total emails scanned
- Number of new emails (not previously recorded in the database)
- Number already scanned (skipped as duplicates)

Report a one-line summary first, for example:
> Scanned 847 emails — 12 new, 835 already seen.

If there are new emails, display them in a table with the following columns:

| Subject | Sender | Date | Attachment |
|---------|--------|------|------------|

- **Attachment**: show "yes" if `has_attachment` is true, "no" otherwise
- Sort rows by Date descending (most recent first)
- Truncate Subject at 60 characters if needed

If zero new emails are found, say so clearly and suggest the user broaden the search window with `--days`.

If the script exits with a non-zero code or prints an error, show the raw error output and stop. Do not attempt to recover or retry automatically.
