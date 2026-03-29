"""Tests for scripts/db.py and scripts/audit.py."""

import json
from pathlib import Path

import pytest

from scripts.db import get_db, upsert, query  # type: ignore
from scripts import audit  # type: ignore


def test_get_db_creates_tables(data_dir):
    conn = get_db(data_dir)
    tables = query(conn, "SELECT name FROM sqlite_master WHERE type='table'")
    table_names = {row["name"] for row in tables}
    assert {"emails", "invoices", "transactions", "matches", "qr_codes"} <= table_names


def test_upsert_and_query(data_dir, sample_transaction):
    conn = get_db(data_dir)
    upsert(conn, "transactions", sample_transaction)

    rows = query(conn, "SELECT * FROM transactions WHERE id = ?", (sample_transaction["id"],))
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == sample_transaction["id"]
    assert row["bank"] == sample_transaction["bank"]
    assert row["date"] == sample_transaction["date"]
    assert abs(row["amount_eur"] - sample_transaction["amount_eur"]) < 0.001
    assert row["description"] == sample_transaction["description"]


def test_upsert_is_idempotent(data_dir, sample_transaction):
    conn = get_db(data_dir)
    upsert(conn, "transactions", sample_transaction)
    upsert(conn, "transactions", sample_transaction)

    rows = query(conn, "SELECT * FROM transactions WHERE id = ?", (sample_transaction["id"],))
    assert len(rows) == 1


def test_audit_log_appends(data_dir):
    audit.log(data_dir, "import", "transaction", "txn_001", {"bank": "abn_amro"})
    audit.log(data_dir, "match_created", "match", "match_001", {"confidence": "confirmed"})

    audit_path = data_dir / "audit.jsonl"
    assert audit_path.exists()

    lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2

    entry1 = json.loads(lines[0])
    assert entry1["action"] == "import"
    assert entry1["entity_type"] == "transaction"
    assert entry1["entity_id"] == "txn_001"
    assert "timestamp" in entry1

    entry2 = json.loads(lines[1])
    assert entry2["action"] == "match_created"
    assert entry2["entity_id"] == "match_001"
