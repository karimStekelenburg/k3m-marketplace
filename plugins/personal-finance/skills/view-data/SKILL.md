---
name: view-data
description: Use when the user wants to view the finance dashboard, see all invoices, check payment status overview, browse transactions, open the data viewer, or launch datasette.
version: 0.1.0
argument-hint: "[--summary-only] [--data-dir PATH]"
allowed-tools: Bash
---

Parse arguments from $ARGUMENTS. Determine the data directory: use `--data-dir` if provided, otherwise default to `~/Documents/finance-data/`.

Run the export/viewer script:

```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/export_db.py [--summary-only] [--data-dir PATH]
```

**Without `--summary-only`** (default behaviour):
The script launches a datasette instance. After the command starts, tell the user:
> Datasette is running at http://localhost:8001 — open this URL in your browser.

The datasette UI exposes all database tables, fully searchable and filterable:
- `invoices` — all parsed invoice records with status and confidence
- `transactions` — imported bank transactions
- `matches` — links between invoices and transactions with confidence levels
- `emails` — scanned inbox messages
- `qr_codes` — generated EPC QR code records

**With `--summary-only`**:
The script prints a text summary to stdout instead of launching datasette. Display the full output from the script verbatim, preserving any table formatting.

**Filtering tip for unpaid invoices:** Tell the user they can find all unpaid invoices in datasette using this SQL query in the datasette query editor:
```sql
SELECT * FROM invoices
WHERE id NOT IN (
  SELECT invoice_id FROM matches WHERE confidence != 'review'
)
```
Direct them to: datasette → top-right menu → "Execute SQL" → paste the query.

If the script exits with a non-zero code or datasette fails to bind the port (e.g. already in use), show the raw error. If the port is in use, suggest the user stop any existing datasette process or specify an alternate port if the script supports it.
