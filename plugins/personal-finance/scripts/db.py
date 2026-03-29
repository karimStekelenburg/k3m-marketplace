"""SQLite database schema and helpers for personal-finance plugin."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS emails (
    id TEXT PRIMARY KEY,
    scanned_at TEXT,
    subject TEXT,
    sender TEXT,
    date TEXT,
    has_attachment INTEGER,
    attachment_names TEXT,
    body_snippet TEXT,
    raw_path TEXT,
    status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS invoices (
    id TEXT PRIMARY KEY,
    email_id TEXT REFERENCES emails(id),
    extracted_at TEXT,
    source_type TEXT,
    extraction_method TEXT,
    vendor TEXT,
    invoice_number TEXT,
    invoice_date TEXT,
    due_date TEXT,
    amount_eur REAL,
    iban TEXT,
    bic TEXT,
    description TEXT,
    raw_path TEXT,
    confidence REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    imported_at TEXT,
    bank TEXT,
    source_file TEXT,
    date TEXT,
    amount_eur REAL,
    counterparty_name TEXT,
    counterparty_iban TEXT,
    description TEXT,
    raw_line TEXT
);

CREATE TABLE IF NOT EXISTS matches (
    id TEXT PRIMARY KEY,
    matched_at TEXT,
    invoice_id TEXT REFERENCES invoices(id),
    transaction_id TEXT REFERENCES transactions(id),
    confidence TEXT,
    match_pass INTEGER,
    reasoning TEXT
);

CREATE TABLE IF NOT EXISTS qr_codes (
    id TEXT PRIMARY KEY,
    generated_at TEXT,
    invoice_id TEXT REFERENCES invoices(id),
    iban TEXT,
    amount_eur REAL,
    vendor TEXT,
    payment_reference TEXT,
    qr_path TEXT
);
"""


def get_db(data_dir: Path) -> sqlite3.Connection:
    """Open or create finance.db in data_dir, apply schema, and return connection."""
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "finance.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    for statement in _SCHEMA.strip().split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(statement)
    conn.commit()
    return conn


def upsert(conn: sqlite3.Connection, table: str, row: dict) -> None:
    """INSERT OR REPLACE a row dict into table."""
    columns = ", ".join(row.keys())
    placeholders = ", ".join("?" for _ in row)
    sql = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
    conn.execute(sql, list(row.values()))
    conn.commit()


def query(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    """Execute sql with params and return results as a list of dicts."""
    cursor = conn.execute(sql, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]
