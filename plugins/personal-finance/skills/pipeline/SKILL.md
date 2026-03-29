---
name: pipeline
description: Use when the user wants to run the full personal finance pipeline, process invoices end-to-end, or be guided through scanning inbox, extracting invoices, importing statements, matching payments, generating QR codes, and viewing results.
version: 0.1.0
argument-hint: "[--data-dir PATH] [--skip STEP,...] [--start-from STEP]"
allowed-tools: Bash, AskUserQuestion, Skill
---

This skill orchestrates the full personal-finance pipeline interactively. It walks the user through each step, asking for input and confirmation before proceeding.

Parse arguments from $ARGUMENTS. Determine the data directory: use `--data-dir` if provided, otherwise default to `~/Documents/finance-data/`.

Optional flags:
- `--skip STEP,...` — comma-separated list of steps to skip (valid: `scan`, `extract`, `import`, `match`, `qr`, `view`)
- `--start-from STEP` — jump to this step and continue from there (same valid values)

## Pipeline overview

Before starting, use `AskUserQuestion` to greet the user and confirm they want to run the pipeline. Show them the steps:

> **Personal Finance Pipeline**
>
> 1. **Scan inbox** — find invoice emails in Apple Mail
> 2. **Extract invoices** — parse PDF attachments for amounts, IBANs, due dates
> 3. **Import statements** — load bank transactions from MT940/CSV files
> 4. **Match payments** — match invoices against transactions
> 5. **Generate QR codes** — create EPC QR codes for unpaid invoices
> 6. **View data** — open the dashboard or print a summary
>
> Data directory: `<resolved path>`

Ask: "Ready to start? You can also skip steps with `--skip` or jump ahead with `--start-from`."

If the user says no or wants to change options, respect that. If yes, proceed.

## Step 1: Scan inbox

Use `AskUserQuestion` to ask:
> **Step 1/6 — Scan Inbox**
> How far back should I search for invoice emails? (default: 90 days)

Accept the user's answer as the `--days` value. Then invoke the scan-inbox skill:

```
/personal-finance:scan-inbox --days <N> --data-dir <PATH>
```

After it completes, show the results. Then use `AskUserQuestion` to ask:
> Found N new emails. Continue to invoice extraction? (yes / no / skip to step N)

## Step 2: Extract invoices

Use `AskUserQuestion` to ask:
> **Step 2/6 — Extract Invoices**
> Extract from all pending emails, or a specific email ID?
> - `all` — process all pending (default)
> - An email ID — process just that one

Then invoke:

```
/personal-finance:extract-invoices <--all-pending or --email-id ID> --data-dir <PATH>
```

The extract-invoices skill handles LLM fallback review internally (it will prompt the user for confirmation on low-confidence extractions).

After completion, use `AskUserQuestion`:
> Extracted N invoices. Continue to bank statement import? (yes / no / skip)

## Step 3: Import bank statements

Use `AskUserQuestion` to ask:
> **Step 3/6 — Import Bank Statements**
> Provide the path to your bank statement file(s) — a single file or a directory.
> Supported formats: MT940 (.mt940, .sta), CSV (.csv)
> Supported banks for CSV: ABN AMRO, ING, Bunq
>
> Enter a file/directory path (or "skip" to skip this step):

If the user provides a path, ask a follow-up if it's a CSV:
> Which bank is this CSV from? (abn_amro / ing / bunq / auto-detect)

Then invoke:

```
/personal-finance:import-statements <PATH> [--bank <BANK>] --data-dir <PATH>
```

If the user has no statements to import, skip gracefully. After completion, use `AskUserQuestion`:
> Imported N transactions. Continue to payment matching? (yes / no / skip)

## Step 4: Match payments

Use `AskUserQuestion` to ask:
> **Step 4/6 — Match Payments**
> Run the matching engine now? It will match invoices against imported transactions.
> - `yes` — run matching (default)
> - `dry-run` — preview matches without writing to database
> - `skip` — skip this step

Then invoke:

```
/personal-finance:match-payments [--dry-run] --data-dir <PATH>
```

The match-payments skill handles "review" confidence matches internally (it will prompt the user for each one).

If the user chose `dry-run`, ask after viewing results:
> Want to run it for real now? (yes / no)

After completion, use `AskUserQuestion`:
> Matching complete. N unmatched invoices remain. Continue to QR code generation? (yes / no / skip)

## Step 5: Generate QR codes

Use `AskUserQuestion` to ask:
> **Step 5/6 — Generate QR Codes**
> Generate EPC QR codes for unpaid invoices?
> - `all` — all unpaid invoices with IBANs (default)
> - An invoice ID — just that one
> - `skip` — skip this step

Then invoke:

```
/personal-finance:generate-qr <--all-unpaid or --invoice-id ID> --data-dir <PATH>
```

After completion, use `AskUserQuestion`:
> Generated N QR codes. View the dashboard? (yes / no)

## Step 6: View data

Use `AskUserQuestion` to ask:
> **Step 6/6 — View Data**
> How would you like to view your data?
> - `dashboard` — launch datasette in the browser (default)
> - `summary` — print a text summary here
> - `skip` — done, skip viewing

Then invoke:

```
/personal-finance:view-data [--summary-only] --data-dir <PATH>
```

## Completion

After the final step (or after the user skips/stops), print a brief recap:

> **Pipeline complete!**
> - Emails scanned: N new
> - Invoices extracted: N
> - Transactions imported: N
> - Matches found: N (N confirmed, N review)
> - QR codes generated: N
> - Unmatched invoices: N

Gather these counts from the outputs of each step that was run. For skipped steps, show "skipped".

## Behavior rules

- **Always ask before proceeding** to the next step. Never silently advance.
- **Respect "skip"** — if the user says skip, move to the next step without running the current one.
- **Respect "no" or "stop"** — if the user says no or wants to stop, end the pipeline gracefully with whatever recap is available.
- **Allow jumping** — if the user says "skip to step N", jump to that step.
- **Errors are not fatal** — if a step fails, show the error, ask the user if they want to retry or skip to the next step.
- **Track state** — keep a running tally of what happened at each step so the final recap is accurate.
