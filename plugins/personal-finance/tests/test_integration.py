"""Full pipeline integration test."""

import json
from pathlib import Path

from scripts.db import get_db, query, upsert  # type: ignore
from scripts.parse_csv import parse_csv_file  # type: ignore
from scripts.parse_mt940 import parse_mt940_file  # type: ignore
from scripts.match_engine import run_matching_and_write  # type: ignore
from scripts.generate_qr import generate_all_pending  # type: ignore
from tests.conftest import FIXTURES_DIR

from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_full_pipeline(data_dir, tmp_path):
    """
    Run the complete pipeline end-to-end using fixture files.
    1. Import ABN AMRO CSV → assert transactions in DB
    2. Import MT940 → assert more transactions in DB
    3. Manually insert a matching invoice into DB
    4. Run match_engine → assert at least 1 confirmed match
    5. Generate QR for unmatched invoices → assert QR files created (if any unmatched)
    6. Assert audit.jsonl has entries
    7. Assert finance.db has data in all relevant tables
    """
    conn = get_db(data_dir)

    # --- Step 1: Import ABN AMRO CSV ---
    abn_txns = parse_csv_file(FIXTURES_DIR / "sample_abn.csv", "abn_amro")
    assert len(abn_txns) >= 5
    for txn in abn_txns:
        row = dict(txn, imported_at=_now_iso())
        upsert(conn, "transactions", row)

    rows_after_abn = query(conn, "SELECT COUNT(*) AS n FROM transactions")
    assert rows_after_abn[0]["n"] >= 5

    # --- Step 2: Import MT940 ---
    mt940_txns = parse_mt940_file(FIXTURES_DIR / "sample.mt940", "abn_amro")
    assert len(mt940_txns) > 0
    for txn in mt940_txns:
        row = dict(txn, imported_at=_now_iso())
        upsert(conn, "transactions", row)

    rows_after_mt940 = query(conn, "SELECT COUNT(*) AS n FROM transactions")
    assert rows_after_mt940[0]["n"] > rows_after_abn[0]["n"]

    # --- Step 3: Insert a matching invoice ---
    # ABN fixture line 1: debit -150.00, counterparty NL91ABNA0417164300
    # MT940 fixture line 1: debit -150.00, with IBAN NL91ABNA0417164300 in description
    # We insert an invoice matching the MT940 first transaction.
    matching_txn_iban = "NL91ABNA0417164300"
    matching_amount = 150.00

    invoice = {
        "id": "pipeline_inv_001",
        "email_id": None,
        "extracted_at": _now_iso(),
        "source_type": "pdf_attachment",
        "extraction_method": "regex",
        "vendor": "Accountantskantoor Jansen",
        "invoice_number": "2024-001",
        "invoice_date": "2024-01-01",
        "due_date": "2024-02-01",
        "amount_eur": matching_amount,
        "iban": matching_txn_iban,
        "bic": "ABNANL2A",
        "description": "Factuur 2024-001 accountantskosten",
        "raw_path": None,
        "confidence": 0.9,
        "notes": None,
    }
    upsert(conn, "invoices", invoice)

    inv_rows = query(conn, "SELECT COUNT(*) AS n FROM invoices")
    assert inv_rows[0]["n"] >= 1

    # --- Step 4: Run matching ---
    summary = run_matching_and_write(data_dir)
    assert summary["confirmed"] >= 1

    match_rows = query(conn, "SELECT * FROM matches WHERE confidence = 'confirmed'")
    assert len(match_rows) >= 1

    # --- Step 5: Generate QR for unmatched invoices ---
    # Add an unmatched invoice (with IBAN and amount, no matching transaction)
    unmatched_invoice = {
        "id": "pipeline_inv_002",
        "email_id": None,
        "extracted_at": _now_iso(),
        "source_type": "pdf_attachment",
        "extraction_method": "regex",
        "vendor": "Onbekend Bedrijf BV",
        "invoice_number": "2024-999",
        "invoice_date": "2024-03-01",
        "due_date": "2024-04-01",
        "amount_eur": 9999.00,
        "iban": "NL02ABNA0123456789",
        "bic": "ABNANL2A",
        "description": "Mysterieuze factuur",
        "raw_path": None,
        "confidence": 0.85,
        "notes": None,
    }
    upsert(conn, "invoices", unmatched_invoice)

    generated = generate_all_pending(data_dir)
    assert len(generated) >= 1
    for rec in generated:
        qr_path = Path(rec["qr_path"])
        assert qr_path.exists(), f"QR file not found: {qr_path}"

    # --- Step 6: Assert audit.jsonl has entries ---
    # run_matching_and_write writes audit entries; generate_all_pending writes audit entries
    audit_path = data_dir / "audit.jsonl"
    assert audit_path.exists()
    lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    # Each line must be valid JSON
    for line in lines:
        entry = json.loads(line)
        assert "action" in entry
        assert "timestamp" in entry

    # --- Step 7: Assert finance.db has data in all relevant tables ---
    for table in ("transactions", "invoices", "matches", "qr_codes"):
        rows = query(conn, f"SELECT COUNT(*) AS n FROM {table}")
        assert rows[0]["n"] >= 1, f"Expected data in table '{table}'"
