"""Multi-pass deterministic invoice-to-transaction matching engine."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.audit import log as audit_log
from scripts.db import get_db, query, upsert

DATA_DIR = Path.home() / "Documents" / "finance-data"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_id(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_date(value: str | None) -> date | None:
    """Parse ISO date string (YYYY-MM-DD) into a date object, or None."""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _iban_eq(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return a.strip().upper() == b.strip().upper()


def _significant_words(text: str | None) -> list[str]:
    """Return words longer than 3 chars from text."""
    if not text:
        return []
    return [w.lower() for w in text.split() if len(w) > 3]


def _fuzzy_name_match(vendor: str | None, counterparty_name: str | None, description: str | None) -> bool:
    """Return True if at least one significant word from vendor appears in counterparty_name or description."""
    haystack = " ".join(filter(None, [counterparty_name, description])).lower()
    for word in _significant_words(vendor):
        if word in haystack:
            return True
    return False


def _vendor_in_description(vendor: str | None, description: str | None) -> bool:
    """Return True if any significant word from vendor appears in description."""
    if not description:
        return False
    desc_lower = description.lower()
    for word in _significant_words(vendor):
        if word in desc_lower:
            return True
    return False


# ---------------------------------------------------------------------------
# Pass implementations
# ---------------------------------------------------------------------------

def _pass1(invoice: dict, txn: dict) -> bool:
    """Confirmed: exact IBAN match + amount within 0.01."""
    return (
        _iban_eq(invoice.get("iban"), txn.get("counterparty_iban"))
        and abs(invoice["amount_eur"] - abs(txn["amount_eur"])) < 0.01
    )


def _pass2(invoice: dict, txn: dict) -> bool:
    """High: exact IBAN match + amount within 0.05."""
    return (
        _iban_eq(invoice.get("iban"), txn.get("counterparty_iban"))
        and abs(invoice["amount_eur"] - abs(txn["amount_eur"])) <= 0.05
    )


def _pass3(invoice: dict, txn: dict) -> bool:
    """Probable: amount within 0.01 + due_date within 10 days of txn date + fuzzy name."""
    if abs(invoice["amount_eur"] - abs(txn["amount_eur"])) >= 0.01:
        return False
    inv_due = _parse_date(invoice.get("due_date"))
    txn_date = _parse_date(txn.get("date"))
    if inv_due is None or txn_date is None:
        return False
    if abs((inv_due - txn_date).days) > 10:
        return False
    return _fuzzy_name_match(
        invoice.get("vendor"),
        txn.get("counterparty_name"),
        txn.get("description"),
    )


def _pass4(invoice: dict, txn: dict) -> bool:
    """Review: amount within 0.01 + vendor word in description."""
    return (
        abs(invoice["amount_eur"] - abs(txn["amount_eur"])) < 0.01
        and _vendor_in_description(invoice.get("vendor"), txn.get("description"))
    )


# ---------------------------------------------------------------------------
# Reasoning generator
# ---------------------------------------------------------------------------

def _make_reasoning(pass_num: int, confidence: str, invoice: dict, txn: dict) -> str:
    amount = invoice.get("amount_eur", 0)
    txn_date = txn.get("date", "unknown date")

    if pass_num == 1:
        return (
            f"Pass 1: IBAN {invoice.get('iban', 'N/A')} + "
            f"amount €{amount:.2f} exact match with transaction {txn_date}"
        )
    if pass_num == 2:
        return (
            f"Pass 2: IBAN {invoice.get('iban', 'N/A')} + "
            f"amount €{amount:.2f} near-match (≤€0.05) with transaction {txn_date}"
        )
    if pass_num == 3:
        inv_due = invoice.get("due_date", "N/A")
        return (
            f"Pass 3: amount €{amount:.2f} + due date {inv_due} within 10 days of {txn_date} "
            f"+ vendor '{invoice.get('vendor', 'N/A')}' fuzzy-matched"
        )
    # pass 4
    return (
        f"Pass 4: amount €{amount:.2f} + vendor '{invoice.get('vendor', 'N/A')}' "
        f"found in description of transaction {txn_date} — requires human review"
    )


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

PASSES = [
    (1, "confirmed", _pass1),
    (2, "high", _pass2),
    (3, "probable", _pass3),
    (4, "review", _pass4),
]


def run_matching(data_dir: Path = DATA_DIR) -> dict:
    """
    Load all unmatched invoices and all transactions from DB.
    Run 4-pass matching.
    Write matches to DB matches table.
    Write audit log entries.
    Returns summary: {"confirmed": N, "high": N, "probable": N, "review": N, "unmatched": N}
    """
    conn = get_db(data_dir)

    # Load all invoices that have amount_eur > 0
    all_invoices = query(conn, "SELECT * FROM invoices WHERE amount_eur > 0")

    # Find already-matched invoice IDs (exclude from matching)
    existing_matches = query(conn, "SELECT invoice_id FROM matches")
    matched_invoice_ids = {r["invoice_id"] for r in existing_matches}

    # Unmatched invoices only
    invoices = [inv for inv in all_invoices if inv["id"] not in matched_invoice_ids]

    # All transactions with amount_eur < 0 (debits/payments)
    all_txns = query(conn, "SELECT * FROM transactions WHERE amount_eur < 0")

    # Find already-used transaction IDs
    existing_txn_matches = query(conn, "SELECT transaction_id FROM matches")
    used_txn_ids: set[str] = {r["transaction_id"] for r in existing_txn_matches}

    summary: dict[str, int] = {"confirmed": 0, "high": 0, "probable": 0, "review": 0, "unmatched": 0}
    new_matches: list[dict] = []

    for invoice in invoices:
        matched = False
        available_txns = [t for t in all_txns if t["id"] not in used_txn_ids]

        for pass_num, confidence, pass_fn in PASSES:
            for txn in available_txns:
                if pass_fn(invoice, txn):
                    reasoning = _make_reasoning(pass_num, confidence, invoice, txn)
                    match_id = _make_id(f"{invoice['id']}:{txn['id']}:{confidence}")
                    match_row = {
                        "id": match_id,
                        "matched_at": _now_iso(),
                        "invoice_id": invoice["id"],
                        "transaction_id": txn["id"],
                        "confidence": confidence,
                        "match_pass": pass_num,
                        "reasoning": reasoning,
                    }
                    new_matches.append(match_row)
                    used_txn_ids.add(txn["id"])
                    summary[confidence] = summary.get(confidence, 0) + 1
                    matched = True
                    break
            if matched:
                break

        if not matched:
            summary["unmatched"] += 1

    return summary, new_matches


def run_matching_and_write(data_dir: Path = DATA_DIR) -> dict:
    """Run matching, write results to DB and audit log, return summary."""
    conn = get_db(data_dir)
    summary, new_matches = run_matching(data_dir)

    for match_row in new_matches:
        upsert(conn, "matches", match_row)
        audit_log(
            data_dir,
            action="match_created",
            entity_type="match",
            entity_id=match_row["id"],
            details={
                "invoice_id": match_row["invoice_id"],
                "transaction_id": match_row["transaction_id"],
                "confidence": match_row["confidence"],
                "match_pass": match_row["match_pass"],
                "reasoning": match_row["reasoning"],
            },
        )

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI: uv run scripts/match_engine.py [--data-dir PATH] [--dry-run]"""
    parser = argparse.ArgumentParser(description="Run invoice-to-transaction matching engine.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Finance data directory")
    parser.add_argument("--dry-run", action="store_true", help="Print matches as JSON without writing to DB")
    args = parser.parse_args()

    data_dir: Path = args.data_dir

    if args.dry_run:
        summary, new_matches = run_matching(data_dir)
        output = {
            "summary": summary,
            "matches": new_matches,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        summary = run_matching_and_write(data_dir)
        print("Matching complete.")
        for key, count in summary.items():
            print(f"  {key}: {count}")


if __name__ == "__main__":
    main()
