---
name: Extract Invoice Data
description: Use when the user wants to extract invoice information from emails, process PDF attachments for invoice data, pull out amounts and IBANs from invoices, or parse invoice PDFs.
version: 0.1.0
argument-hint: "[--email-id ID | --all-pending] [--data-dir PATH]"
allowed-tools: Bash
---

Determine the data directory: use `--data-dir` if provided, otherwise default to `~/Documents/finance-data/`.

Determine the extraction scope from the user's arguments:

**If `--email-id ID` is given:**
Run the extractor for that single email's attachment:
```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/extract_invoice.py --email-id ID [--data-dir PATH]
```

**If `--all-pending` is given (or no scope flag is provided):**
Run the extractor over all emails with `status='pending'` in the database:
```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/extract_invoice.py --all-pending [--data-dir PATH]
```

After the script completes, report:
- Total invoices processed
- How many succeeded with high confidence (no fallback)
- How many used `llm_fallback` (flag these clearly — they require review)

Display a summary table for all extracted invoices:

| Email ID | Vendor | Amount | Due Date | Confidence | LLM Fallback |
|----------|--------|--------|----------|------------|--------------|

Mark `llm_fallback` rows with a warning indicator.

**For each `llm_fallback` invoice**, perform manual extraction:
1. Show the raw extracted text from the script's output for that invoice
2. Read the text carefully and extract: vendor name, invoice number, total amount (with currency), IBAN, and due date
3. Present your extracted values to the user for confirmation
4. Once confirmed (or if the values are unambiguous), write the corrected fields to the database by running:
   ```
   uv run ${CLAUDE_PLUGIN_ROOT}/scripts/extract_invoice.py --update-record --email-id ID --vendor "..." --amount ... --due-date ... --iban ... [--data-dir PATH]
   ```
5. Mark the record's `llm_fallback` flag as resolved after writing

If any attachment cannot be read (corrupt PDF, unsupported format), report the email ID and error; continue processing remaining items.
