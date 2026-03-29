"""Parse CSV bank statement exports from Dutch banks (ABN AMRO, ING, Bunq)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

DATA_DIR = Path.home() / "Documents" / "finance-data"

IBAN_RE = re.compile(r"\b([A-Z]{2}[0-9]{2}[A-Z0-9]{4,30})\b")


def _make_id(bank: str, date: str, amount: float, description: str) -> str:
    raw = f"{bank}|{date}|{amount}|{description}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _extract_iban(text: str) -> str:
    m = IBAN_RE.search(text)
    return m.group(1) if m else ""


def _read_bytes(file_path: Path) -> bytes:
    return file_path.read_bytes()


def _decode(raw: bytes, preferred: str = "utf-8") -> tuple[str, str]:
    """Try preferred encoding first, then windows-1252, then chardet fallback."""
    for enc in (preferred, "windows-1252", "utf-8-sig"):
        try:
            return raw.decode(enc), enc
        except (UnicodeDecodeError, LookupError):
            pass
    # Last resort: chardet
    try:
        import chardet

        detected = chardet.detect(raw)
        enc = detected.get("encoding") or "utf-8"
        return raw.decode(enc, errors="replace"), enc
    except ImportError:
        return raw.decode("utf-8", errors="replace"), "utf-8"


def _parse_amount_comma(value: str) -> float:
    """Parse amount string with comma decimal separator."""
    return float(value.replace(".", "").replace(",", "."))


def _parse_abn_amro(text: str, file_name: str) -> list[dict]:
    """
    ABN AMRO tab-separated CSV.
    Columns (0-indexed): account_number, currency, date(YYYYMMDD),
    balance_before, balance_after, date2, amount, description
    """
    results: list[dict] = []
    reader = csv.reader(io.StringIO(text), delimiter="\t")
    for row in reader:
        if not row or len(row) < 8:
            continue
        # Skip header row if present (first column is not an IBAN-like account number)
        # ABN AMRO account numbers start with NL followed by digits
        first_col = row[0].strip()
        if not re.match(r"^NL\d{2}", first_col):
            continue

        raw_date = row[2].strip()
        if len(raw_date) != 8 or not raw_date.isdigit():
            continue
        date_str = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"

        try:
            amount_eur = _parse_amount_comma(row[6].strip())
        except ValueError:
            continue

        description = row[7].strip() if len(row) > 7 else ""
        counterparty_iban = _extract_iban(description)
        # ABN AMRO may embed NAME/ in description
        name_m = re.search(r"NAME/([^/\n]+)", description)
        counterparty_name = name_m.group(1).strip() if name_m else ""

        txn_id = _make_id("abn_amro", date_str, amount_eur, description)

        results.append(
            {
                "id": txn_id,
                "bank": "abn_amro",
                "source_file": file_name,
                "date": date_str,
                "amount_eur": amount_eur,
                "counterparty_name": counterparty_name,
                "counterparty_iban": counterparty_iban,
                "description": description,
                "raw_line": repr(row),
            }
        )
    return results


def _parse_ing(text: str, file_name: str) -> list[dict]:
    """
    ING CSV with Dutch headers.
    Datum, Naam / Omschrijving, Rekening, Tegenrekening, Code,
    Af of Bij, Bedrag (EUR), Mutatiesoort, Mededelingen
    """
    results: list[dict] = []
    reader = csv.DictReader(io.StringIO(text), delimiter=",")
    for row in reader:
        raw_date = row.get("Datum", "").strip()
        if not raw_date:
            continue
        # DD-MM-YYYY -> YYYY-MM-DD
        parts = raw_date.split("-")
        if len(parts) == 3:
            date_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
        else:
            date_str = raw_date

        af_of_bij = row.get("Af of Bij", "").strip()
        raw_amount = row.get("Bedrag (EUR)", "0").strip()
        try:
            amount_eur = _parse_amount_comma(raw_amount)
        except ValueError:
            continue
        if af_of_bij.lower() == "af":
            amount_eur = -abs(amount_eur)
        else:
            amount_eur = abs(amount_eur)

        description = row.get("Mededelingen", "").strip()
        counterparty_iban = row.get("Tegenrekening", "").strip()
        if not counterparty_iban:
            counterparty_iban = _extract_iban(description)
        counterparty_name = row.get("Naam / Omschrijving", "").strip()

        txn_id = _make_id("ing", date_str, amount_eur, description)

        results.append(
            {
                "id": txn_id,
                "bank": "ing",
                "source_file": file_name,
                "date": date_str,
                "amount_eur": amount_eur,
                "counterparty_name": counterparty_name,
                "counterparty_iban": counterparty_iban,
                "description": description,
                "raw_line": repr(dict(row)),
            }
        )
    return results


def _parse_bunq(text: str, file_name: str) -> list[dict]:
    """
    Bunq CSV: Date, Amount, Account, Counterpart, Name, Description, Category, Balance
    """
    results: list[dict] = []
    reader = csv.DictReader(io.StringIO(text), delimiter=",")
    for row in reader:
        date_str = row.get("Date", "").strip()
        if not date_str:
            continue

        raw_amount = row.get("Amount", "0").strip()
        try:
            amount_eur = float(raw_amount)
        except ValueError:
            continue

        description = row.get("Description", "").strip()
        counterparty_iban = row.get("Counterpart", "").strip()
        if not counterparty_iban:
            counterparty_iban = _extract_iban(description)
        counterparty_name = row.get("Name", "").strip()

        txn_id = _make_id("bunq", date_str, amount_eur, description)

        results.append(
            {
                "id": txn_id,
                "bank": "bunq",
                "source_file": file_name,
                "date": date_str,
                "amount_eur": amount_eur,
                "counterparty_name": counterparty_name,
                "counterparty_iban": counterparty_iban,
                "description": description,
                "raw_line": repr(dict(row)),
            }
        )
    return results


def detect_bank(file_path: Path) -> str:
    """
    Heuristic: auto-detect which bank the CSV is from by reading the first few lines.
    Returns 'abn_amro' | 'ing' | 'bunq'.
    """
    raw = _read_bytes(file_path)
    text, _ = _decode(raw, preferred="utf-8")
    first_lines = text[:2000]

    if "Datum" in first_lines and "Naam / Omschrijving" in first_lines:
        return "ing"
    if "Counterpart" in first_lines and "Date" in first_lines:
        return "bunq"
    return "abn_amro"


def parse_csv_file(file_path: Path, bank: str) -> list[dict]:
    """
    Parse a CSV bank statement. bank must be 'abn_amro', 'ing', or 'bunq'.
    Returns normalized transaction dicts.
    Raises ValueError if bank is not recognized.
    """
    valid_banks = {"abn_amro", "ing", "bunq"}
    if bank not in valid_banks:
        raise ValueError(f"Unknown bank '{bank}'. Must be one of: {valid_banks}")

    raw = _read_bytes(file_path)
    preferred = "utf-8" if bank in ("ing", "bunq") else "windows-1252"
    text, _ = _decode(raw, preferred=preferred)

    if bank == "abn_amro":
        return _parse_abn_amro(text, file_path.name)
    elif bank == "ing":
        return _parse_ing(text, file_path.name)
    else:
        return _parse_bunq(text, file_path.name)


def main() -> None:
    """CLI: uv run scripts/parse_csv.py <file.csv> [--bank abn_amro|ing|bunq] [--data-dir PATH] [--dry-run]"""
    parser = argparse.ArgumentParser(description="Parse CSV bank statement exports.")
    parser.add_argument("file", type=Path, help="Path to CSV file")
    parser.add_argument(
        "--bank",
        choices=["abn_amro", "ing", "bunq"],
        default=None,
        help="Bank identifier (auto-detected if omitted)",
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

    bank = args.bank or detect_bank(file_path)
    print(f"Detected bank: {bank}", file=sys.stderr)

    transactions = parse_csv_file(file_path, bank)

    if args.dry_run:
        print(json.dumps(transactions, indent=2, ensure_ascii=False, default=str))
        return

    # Write to DB
    try:
        from scripts.db import get_db, upsert
        from scripts.audit import log as audit_log
    except ImportError:
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
