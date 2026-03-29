"""Tests for scripts/match_engine.py — multi-pass matching logic."""

import pytest

from scripts.db import get_db, upsert  # type: ignore
from scripts.match_engine import run_matching_and_write  # type: ignore


def _seed_invoice(conn, overrides=None):
    invoice = {
        "id": "inv_001",
        "email_id": None,
        "extracted_at": "2026-01-15T10:00:00Z",
        "source_type": "pdf_attachment",
        "extraction_method": "regex",
        "vendor": "Accountantskantoor Jansen",
        "invoice_number": "2024-001",
        "invoice_date": "2024-01-10",
        "due_date": "2024-02-10",
        "amount_eur": 363.00,
        "iban": "NL91ABNA0417164300",
        "bic": "ABNANL2A",
        "description": "Factuur 2024-001 accountantskosten",
        "raw_path": None,
        "confidence": 0.9,
        "notes": None,
    }
    if overrides:
        invoice.update(overrides)
    upsert(conn, "invoices", invoice)
    return invoice


def _seed_transaction(conn, overrides=None):
    txn = {
        "id": "txn_001",
        "imported_at": "2026-01-20T10:00:00Z",
        "bank": "abn_amro",
        "source_file": "sample.csv",
        "date": "2024-01-15",
        "amount_eur": -363.00,
        "counterparty_name": "Accountantskantoor Jansen",
        "counterparty_iban": "NL91ABNA0417164300",
        "description": "Betaling factuur 2024-001",
        "raw_line": "raw",
    }
    if overrides:
        txn.update(overrides)
    upsert(conn, "transactions", txn)
    return txn


def test_pass1_confirmed_match(data_dir):
    conn = get_db(data_dir)
    _seed_invoice(conn)
    _seed_transaction(conn)

    summary = run_matching_and_write(data_dir)
    assert summary["confirmed"] == 1


def test_pass2_high_match(data_dir):
    conn = get_db(data_dir)
    _seed_invoice(conn)
    # Amount differs by €0.02 — too far for pass1 (needs < 0.01), within pass2 (≤ 0.05)
    _seed_transaction(conn, {"amount_eur": -363.02})

    summary = run_matching_and_write(data_dir)
    assert summary["high"] == 1
    assert summary["confirmed"] == 0


def test_pass3_probable_match(data_dir):
    conn = get_db(data_dir)
    # Invoice with no IBAN, same amount, vendor that fuzzy-matches counterparty
    _seed_invoice(conn, {
        "iban": None,
        "bic": None,
        "due_date": "2024-01-16",  # within 10 days of txn date 2024-01-15
    })
    _seed_transaction(conn, {
        "counterparty_iban": "NL99FAKE0000000000",  # different IBAN so pass1/2 fail
        "counterparty_name": "Accountantskantoor Jansen",
    })

    summary = run_matching_and_write(data_dir)
    assert summary["probable"] == 1


def test_no_match_different_amount(data_dir):
    conn = get_db(data_dir)
    _seed_invoice(conn)
    # Amount differs by €50 — no pass should match
    _seed_transaction(conn, {"amount_eur": -413.00, "counterparty_iban": "NL91ABNA0417164300"})

    summary = run_matching_and_write(data_dir)
    assert summary.get("confirmed", 0) == 0
    assert summary.get("high", 0) == 0
    assert summary.get("probable", 0) == 0
    assert summary["unmatched"] >= 1


def test_transaction_not_reused(data_dir):
    conn = get_db(data_dir)
    # Two invoices competing for the same transaction
    _seed_invoice(conn, {"id": "inv_001", "vendor": "Accountantskantoor Jansen"})
    _seed_invoice(conn, {"id": "inv_002", "vendor": "Accountantskantoor Jansen"})
    _seed_transaction(conn)  # Only one transaction

    summary = run_matching_and_write(data_dir)
    total_matched = (
        summary.get("confirmed", 0)
        + summary.get("high", 0)
        + summary.get("probable", 0)
        + summary.get("review", 0)
    )
    assert total_matched == 1
    assert summary["unmatched"] == 1


def test_debit_only_matched(data_dir):
    conn = get_db(data_dir)
    _seed_invoice(conn)
    # Credit transaction (positive amount) — should NOT be matched
    _seed_transaction(conn, {"amount_eur": 363.00})

    summary = run_matching_and_write(data_dir)
    assert summary.get("confirmed", 0) == 0
    assert summary["unmatched"] == 1


def test_run_matching_returns_summary(data_dir):
    conn = get_db(data_dir)
    _seed_invoice(conn)
    _seed_transaction(conn)

    summary = run_matching_and_write(data_dir)
    for key in ("confirmed", "high", "probable", "review", "unmatched"):
        assert key in summary, f"Missing key '{key}' in summary"
