---
name: generate-qr
description: Use when the user wants to generate QR codes for unpaid invoices, create payment QR codes to scan with a banking app, or produce EPC QR codes for outstanding invoices.
version: 0.1.0
argument-hint: "[--invoice-id ID | --all-unpaid] [--data-dir PATH]"
allowed-tools: Bash
---

Parse arguments from $ARGUMENTS. Determine the data directory: use `--data-dir` if provided, otherwise default to `~/Documents/finance-data/`.

Determine the generation scope:

**If `--invoice-id ID` is given:**
```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_qr.py --invoice-id ID [--data-dir PATH]
```

**If `--all-unpaid` is given (or no scope flag is provided):**
```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_qr.py --all-unpaid [--data-dir PATH]
```

After the script completes, report how many QR codes were generated and where they were saved.

Display a summary table for all processed invoices:

| Invoice ID | Vendor | Amount | Due Date | IBAN | QR File Path |
|------------|--------|--------|----------|------|--------------|

- **QR File Path**: show the absolute path to the generated PNG file
- For invoices where QR generation succeeded, show the path
- For invoices where generation failed, show the reason in the QR File Path column

**Compatibility note:** Inform the user that the generated EPC QR codes are compatible with ING, ABN AMRO, Bunq, and any other SEPA-compliant banking app that supports the EPC QR standard. Scanning the code in the banking app pre-fills the beneficiary IBAN, amount, and payment reference.

**Missing IBAN warning:** If any invoice has no IBAN recorded in the database, warn the user explicitly for each affected invoice:
> Warning: Invoice `<ID>` (Vendor: `<vendor>`, Amount: `<amount>`) has no IBAN — QR code cannot be generated. This invoice must be paid manually.

List all no-IBAN invoices together at the end of the output so the user can act on them.

If the script exits with a non-zero code, show the raw error and stop.
