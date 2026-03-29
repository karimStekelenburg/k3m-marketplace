"""Generate EPC QR codes for unpaid invoices."""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import segno
import segno.helpers

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


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def generate_epc_qr(invoice: dict, output_dir: Path) -> Path:
    """
    Generate an EPC QR code PNG for a single invoice.

    Uses segno.helpers.make_epc_qr():
      - name: invoice['vendor'] (max 70 chars, truncate if needed)
      - iban: invoice['iban']
      - amount: invoice['amount_eur']
      - text: invoice['description'] or invoice['invoice_number'] (max 140 chars)
      - bic: invoice['bic'] if present, else omit

    Saves to output_dir/qr_{invoice_id}.png at scale=10.
    Returns path to saved PNG.

    Raises ValueError if invoice has no IBAN or amount <= 0.
    """
    iban = invoice.get("iban")
    if not iban:
        raise ValueError(f"Invoice {invoice.get('id')} has no IBAN")

    amount = invoice.get("amount_eur", 0)
    if amount <= 0:
        raise ValueError(f"Invoice {invoice.get('id')} has non-positive amount: {amount}")

    vendor = (invoice.get("vendor") or "")[:70]
    text_raw = invoice.get("description") or invoice.get("invoice_number") or ""
    text = str(text_raw)[:140]

    bic = invoice.get("bic") or None

    kwargs: dict = {
        "name": vendor,
        "iban": iban,
        "amount": amount,
        "text": text,
    }
    if bic:
        kwargs["bic"] = bic

    qr = segno.helpers.make_epc_qr(**kwargs)

    output_dir.mkdir(parents=True, exist_ok=True)
    invoice_id = invoice.get("id", _make_id(f"{iban}:{amount}"))
    out_path = output_dir / f"qr_{invoice_id}.png"
    qr.save(str(out_path), scale=10)
    return out_path


def generate_all_pending(data_dir: Path = DATA_DIR) -> list[dict]:
    """
    Query DB for all invoices that:
    - Have no entry in matches table (unmatched), OR
    - Have only 'review' confidence matches
    - AND have a non-null IBAN and amount_eur > 0

    Generate QR for each. Write to qr_codes table. Audit log each.
    Returns list of generated qr_code records.
    """
    conn = get_db(data_dir)
    output_dir = data_dir / "qr"

    # Invoices with amount > 0 and a non-null IBAN
    invoices = query(
        conn,
        "SELECT * FROM invoices WHERE amount_eur > 0 AND iban IS NOT NULL AND iban != ''",
    )

    # Build a map: invoice_id -> list of confidence levels in matches
    all_matches = query(conn, "SELECT invoice_id, confidence FROM matches")
    match_confidences: dict[str, list[str]] = {}
    for m in all_matches:
        match_confidences.setdefault(m["invoice_id"], []).append(m["confidence"])

    # Filter: unmatched OR only 'review' matches
    pending = []
    for inv in invoices:
        confidences = match_confidences.get(inv["id"], [])
        if not confidences or all(c == "review" for c in confidences):
            pending.append(inv)

    generated: list[dict] = []

    for invoice in pending:
        try:
            qr_path = generate_epc_qr(invoice, output_dir)
        except (ValueError, Exception) as exc:
            audit_log(
                data_dir,
                action="qr_generation_failed",
                entity_type="invoice",
                entity_id=invoice.get("id", "unknown"),
                details={"error": str(exc)},
            )
            continue

        qr_id = _make_id(f"qr:{invoice['id']}:{_now_iso()}")
        payment_reference = invoice.get("description") or invoice.get("invoice_number") or ""

        qr_record = {
            "id": qr_id,
            "generated_at": _now_iso(),
            "invoice_id": invoice["id"],
            "iban": invoice.get("iban"),
            "amount_eur": invoice.get("amount_eur"),
            "vendor": invoice.get("vendor"),
            "payment_reference": str(payment_reference)[:140],
            "qr_path": str(qr_path),
        }

        upsert(conn, "qr_codes", qr_record)
        audit_log(
            data_dir,
            action="qr_generated",
            entity_type="qr_code",
            entity_id=qr_id,
            details={
                "invoice_id": invoice["id"],
                "vendor": invoice.get("vendor"),
                "amount_eur": invoice.get("amount_eur"),
                "qr_path": str(qr_path),
            },
        )
        generated.append(qr_record)

    return generated


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI: uv run scripts/generate_qr.py [--data-dir PATH] [--invoice-id ID]"""
    parser = argparse.ArgumentParser(description="Generate EPC QR codes for unpaid invoices.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Finance data directory")
    parser.add_argument("--invoice-id", type=str, default=None, help="Generate QR for a specific invoice ID only")
    args = parser.parse_args()

    data_dir: Path = args.data_dir

    if args.invoice_id:
        conn = get_db(data_dir)
        rows = query(conn, "SELECT * FROM invoices WHERE id = ?", (args.invoice_id,))
        if not rows:
            print(f"Invoice not found: {args.invoice_id}", file=sys.stderr)
            sys.exit(1)
        invoice = rows[0]
        output_dir = data_dir / "qr"
        try:
            qr_path = generate_epc_qr(invoice, output_dir)
            print(f"QR code saved: {qr_path}")
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        records = generate_all_pending(data_dir)
        print(f"Generated {len(records)} QR code(s).")
        for rec in records:
            print(f"  {rec['vendor']} | €{rec['amount_eur']:.2f} | {rec['qr_path']}")


if __name__ == "__main__":
    main()
