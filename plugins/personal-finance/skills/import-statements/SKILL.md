---
name: Import Bank Statements
description: Use when the user wants to import bank statements, parse MT940 files, load CSV exports from ABN AMRO, ING or Bunq, or add transactions to the finance database.
version: 0.1.0
argument-hint: "<file_or_directory> [--bank abn_amro|ing|bunq] [--data-dir PATH]"
allowed-tools: Bash
---

Determine the data directory: use `--data-dir` if provided, otherwise default to `~/Documents/finance-data/`.

Accept the positional argument as a file path or directory path containing bank statement files. If no path is given, ask the user to provide one before proceeding.

**Format detection:** For each file to process, determine the parser based on the file extension:
- Extension `.mt940` or `.sta` → MT940 format
- Any other extension (`.csv`, `.txt`, etc.) → CSV format

If `--bank` is specified, pass it to the CSV parser to apply bank-specific column mappings (supported values: `abn_amro`, `ing`, `bunq`). If the bank cannot be detected automatically from CSV headers, prompt the user to specify `--bank`.

**For each file, run the appropriate parser:**

MT940:
```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/parse_mt940.py <file> [--data-dir PATH]
```

CSV:
```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/parse_csv.py <file> [--bank BANK] [--data-dir PATH]
```

Collect results across all files. After all files are processed, report:

| Bank | File | Transactions Added | Date Range | Parse Errors |
|------|------|--------------------|------------|--------------|

- **Transactions Added**: count of new rows inserted into the database
- **Date Range**: earliest to latest transaction date in the file
- **Parse Errors**: number of rows skipped due to parse failures; list the specific row numbers or error messages if any exist

**Duplicate detection:** If the parser reports that a transaction ID was already present in the database, warn the user explicitly:
> Warning: N duplicate transaction(s) detected in `<filename>` — already in database, skipped.

Do not silently skip duplicates. Show the transaction IDs that were skipped so the user can verify.

If a file does not exist or cannot be read, report the error and continue with the remaining files.
