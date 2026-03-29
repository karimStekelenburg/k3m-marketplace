"""Parse MT940 bank statement files using the mt940 library."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import mt940

DATA_DIR = Path.home() / "Documents" / "finance-data"

IBAN_RE = re.compile(r"\b([A-Z]{2}[0-9]{2}[A-Z0-9]{4,30})\b")


def _make_id(bank: str, date: str, amount: float, description: str) -> str:
    raw = f"{bank}|{date}|{amount}|{description}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _extract_iban(text: str) -> str:
    m = IBAN_RE.search(text)
    return m.group(1) if m else ""


def _extract_name(description: str, bank: str) -> str:
    """Extract counterparty name from structured MT940 remittance info."""
    # Try /NAME/ tag (common in SEPA structured format)
    m = re.search(r"/NAME/([^/]+)", description)
    if m:
        return m.group(1).strip()
    # ABN AMRO sometimes uses NAME/ without leading slash
    m = re.search(r"NAME/([^/]+)", description)
    if m:
        return m.group(1).strip()
    # /BENM/ tag used by some banks for beneficiary name
    m = re.search(r"/BENM//NAME/([^/]+)", description)
    if m:
        return m.group(1).strip()
    return ""


def parse_mt940_file(file_path: Path, bank: str) -> list[dict]:
    """
    Parse an MT940 file. Returns list of normalized transaction dicts.

    Each dict has keys: id, bank, source_file, date, amount_eur,
    counterparty_name, counterparty_iban, description, raw_line.
    """
    transactions_parsed = mt940.parse(str(file_path))
    results: list[dict] = []

    for txn in transactions_parsed:
        data = txn.data

        # Amount
        amount_decimal = data.get("amount")
        if amount_decimal is None:
            continue
        amount_eur = float(amount_decimal.amount)

        # Date
        date_obj = data.get("date")
        if date_obj is None:
            continue
        if hasattr(date_obj, "isoformat"):
            date_str = date_obj.isoformat()
        else:
            date_str = str(date_obj)

        # Description: combine transaction_details and extra_details
        details = str(data.get("transaction_details", "") or "")
        extra = str(data.get("extra_details", "") or "")
        description = " ".join(filter(None, [details, extra])).strip()

        counterparty_iban = _extract_iban(description)
        counterparty_name = _extract_name(description, bank)

        txn_id = _make_id(bank, date_str, amount_eur, description)

        results.append(
            {
                "id": txn_id,
                "bank": bank,
                "source_file": file_path.name,
                "date": date_str,
                "amount_eur": amount_eur,
                "counterparty_name": counterparty_name,
                "counterparty_iban": counterparty_iban,
                "description": description,
                "raw_line": repr(dict(data)),
            }
        )

    return results


def main() -> None:
    """CLI: uv run scripts/parse_mt940.py <file.mt940> --bank abn_amro|ing|bunq [--data-dir PATH] [--dry-run]"""
    parser = argparse.ArgumentParser(description="Parse MT940 bank statement files.")
    parser.add_argument("file", type=Path, help="Path to .mt940 file")
    parser.add_argument(
        "--bank",
        required=True,
        choices=["abn_amro", "ing", "bunq"],
        help="Bank identifier",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help=f"Data directory (default: {DATA_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print transactions as JSON without writing to DB",
    )
    args = parser.parse_args()

    file_path: Path = args.file
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    transactions = parse_mt940_file(file_path, args.bank)

    if args.dry_run:
        print(json.dumps(transactions, indent=2, ensure_ascii=False, default=str))
        return

    # Write to DB
    try:
        from scripts.db import get_db, upsert
        from scripts.audit import log as audit_log
    except ImportError:
        # Fallback when run directly as a script
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from scripts.db import get_db, upsert
        from scripts.audit import log as audit_log

    from datetime import datetime, timezone

    data_dir: Path = args.data_dir
    conn = get_db(data_dir)
    imported_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for txn in transactions:
        row = dict(txn, imported_at=imported_at)
        upsert(conn, "transactions", row)
        audit_log(
            data_dir,
            action="import",
            entity_type="transaction",
            entity_id=txn["id"],
            details={"source_file": txn["source_file"], "bank": txn["bank"]},
        )

    print(f"Imported {len(transactions)} transaction(s) from {file_path.name}.")


if __name__ == "__main__":
    main()
