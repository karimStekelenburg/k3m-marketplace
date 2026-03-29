---
name: Match Invoices to Payments
description: Use when the user wants to match invoices against bank transactions, find which invoices have been paid, check payment status, or run the payment matching engine.
version: 0.1.0
argument-hint: "[--data-dir PATH] [--dry-run]"
allowed-tools: Bash
---

Determine the data directory: use `--data-dir` if provided, otherwise default to `~/Documents/finance-data/`.

Run the matching engine, passing `--dry-run` if the user requested it (dry-run shows what would be matched without writing to the database):

```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/match_engine.py [--dry-run] [--data-dir PATH]
```

After the script completes, display the matching summary table:

| Confidence | Count | Meaning |
|------------|-------|---------|
| confirmed  | N     | IBAN + exact amount |
| high       | N     | IBAN + amount within €0.05 |
| probable   | N     | Amount + date + fuzzy vendor name |
| review     | N     | Amount + description keyword match — HUMAN REVIEW REQUIRED |
| unmatched  | N     | No match found |

If `--dry-run` was used, note that no changes were written.

**For "review" confidence matches**, do not silently accept them. For each one, show:
- Invoice: vendor, amount, due date, invoice number
- Candidate transaction: bank, date, amount, description

Then ask the user explicitly:
> Does this transaction match this invoice? (yes / no / skip)

Wait for the user's response for each review item before continuing. If the user confirms, write the match to the database. If rejected, leave the invoice as unmatched. If skipped, leave it in review state.

**For unmatched invoices**, list them in a table:

| Invoice ID | Vendor | Amount | Due Date | IBAN Available |
|------------|--------|--------|----------|----------------|

Note that unmatched invoices with a known IBAN are candidates for QR code generation. Suggest running the `generate-qr` skill for those.

If the script exits with an error, display the raw error output and stop.
