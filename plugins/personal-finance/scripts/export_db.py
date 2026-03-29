"""Utility to print finance data summary and launch datasette."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.db import get_db, query

DATA_DIR = Path.home() / "Documents" / "finance-data"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_data_dir(data_dir: Path = DATA_DIR) -> None:
    """Create data_dir and qr/ subdirectory if they don't exist."""
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "qr").mkdir(parents=True, exist_ok=True)


def print_summary(data_dir: Path = DATA_DIR) -> None:
    """
    Print a text summary to stdout:
    - Total invoices (by status: unmatched, confirmed, high, probable, review)
    - Total transactions
    - Total matches by confidence
    - Total QR codes generated
    - Data directory path
    - Command to launch datasette
    """
    ensure_data_dir(data_dir)
    conn = get_db(data_dir)

    # --- Invoices ---
    all_invoices = query(conn, "SELECT id FROM invoices")
    total_invoices = len(all_invoices)

    # Gather per-invoice best confidence
    all_matches = query(conn, "SELECT invoice_id, confidence FROM matches")
    invoice_confidences: dict[str, list[str]] = {}
    for m in all_matches:
        invoice_confidences.setdefault(m["invoice_id"], []).append(m["confidence"])

    confidence_order = ["confirmed", "high", "probable", "review"]
    invoice_status: dict[str, int] = {c: 0 for c in confidence_order}
    invoice_status["unmatched"] = 0

    for inv in all_invoices:
        inv_id = inv["id"]
        confidences = invoice_confidences.get(inv_id, [])
        if not confidences:
            invoice_status["unmatched"] += 1
        else:
            # Use best confidence level (lowest pass number wins)
            best = None
            for c in confidence_order:
                if c in confidences:
                    best = c
                    break
            if best:
                invoice_status[best] += 1
            else:
                invoice_status["unmatched"] += 1

    # --- Transactions ---
    txn_count_rows = query(conn, "SELECT COUNT(*) AS cnt FROM transactions")
    total_transactions = txn_count_rows[0]["cnt"] if txn_count_rows else 0

    # --- Matches by confidence ---
    match_rows = query(conn, "SELECT confidence, COUNT(*) AS cnt FROM matches GROUP BY confidence")
    matches_by_confidence = {r["confidence"]: r["cnt"] for r in match_rows}

    # --- QR codes ---
    qr_count_rows = query(conn, "SELECT COUNT(*) AS cnt FROM qr_codes")
    total_qr = qr_count_rows[0]["cnt"] if qr_count_rows else 0

    db_path = data_dir / "finance.db"
    datasette_cmd = f"uv run datasette {db_path} --open"

    # --- Print ---
    print("=" * 60)
    print("  Personal Finance — Data Summary")
    print("=" * 60)
    print(f"\nInvoices ({total_invoices} total):")
    for status in confidence_order:
        print(f"  {status:<12} {invoice_status[status]}")
    print(f"  {'unmatched':<12} {invoice_status['unmatched']}")

    print(f"\nTransactions: {total_transactions}")

    print("\nMatches by confidence:")
    if matches_by_confidence:
        for conf in confidence_order:
            count = matches_by_confidence.get(conf, 0)
            print(f"  {conf:<12} {count}")
    else:
        print("  (none)")

    print(f"\nQR codes generated: {total_qr}")
    print(f"\nData directory: {data_dir}")
    print(f"\nLaunch datasette:\n  {datasette_cmd}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Datasette launcher
# ---------------------------------------------------------------------------

def launch_datasette(data_dir: Path = DATA_DIR) -> None:
    """
    Launch datasette for finance.db using subprocess.
    Command: uv run datasette <data_dir>/finance.db --open
    """
    db_path = data_dir / "finance.db"
    if not db_path.exists():
        print(f"Database not found: {db_path}", file=sys.stderr)
        print("Run an import or scan first to create the database.", file=sys.stderr)
        sys.exit(1)

    cmd = ["uv", "run", "datasette", str(db_path), "--open"]
    print(f"Launching: {' '.join(cmd)}")
    subprocess.run(cmd, check=False)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """
    CLI: uv run scripts/export_db.py [--data-dir PATH] [--summary-only]
    Default: print summary then launch datasette.
    --summary-only: just print the summary, don't launch datasette.
    """
    parser = argparse.ArgumentParser(description="Finance data summary and datasette launcher.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Finance data directory")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print summary only, do not launch datasette",
    )
    args = parser.parse_args()

    data_dir: Path = args.data_dir
    ensure_data_dir(data_dir)
    print_summary(data_dir)

    if not args.summary_only:
        launch_datasette(data_dir)


if __name__ == "__main__":
    main()
