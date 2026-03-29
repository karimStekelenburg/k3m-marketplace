"""Extract invoice fields from PDF files and HTML email bodies."""

from __future__ import annotations

import argparse
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from scripts import audit, db

DATA_DIR = Path.home() / "Documents" / "finance-data"

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

_RE_IBAN = re.compile(r"[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}")
_RE_AMOUNT_PREFIX = re.compile(r"(?:EUR|€)\s*(\d{1,6}[.,]\d{2})")
_RE_AMOUNT_SUFFIX = re.compile(r"(\d{1,6}[.,]\d{2})\s*(?:EUR|€)")
_RE_INVOICE_NUMBER = re.compile(
    r"(?:factuur|invoice|factuurnummer|invoice\s*(?:no|number|#)?)[:\s#]*([A-Z0-9\-]{3,30})",
    re.IGNORECASE,
)
_RE_DUE_DATE = re.compile(
    r"(?:vervaldatum|due\s*date|betaal\s*voor)[:\s]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})",
    re.IGNORECASE,
)
_RE_INVOICE_DATE = re.compile(
    r"(?:factuurdatum|invoice\s*date|datum)[:\s]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})",
    re.IGNORECASE,
)
_RE_BIC = re.compile(r"\b([A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?)\b")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize_amount(raw: str) -> float | None:
    """Convert Dutch/European amount string to float."""
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


def _extract_fields_from_text(text: str) -> dict:
    """Apply all regex patterns to plain text and return extracted fields."""
    fields: dict = {
        "vendor": None,
        "invoice_number": None,
        "invoice_date": None,
        "due_date": None,
        "amount_eur": None,
        "iban": None,
        "bic": None,
        "description": None,
    }

    # IBAN
    m = _RE_IBAN.search(text)
    if m:
        fields["iban"] = m.group(0)

    # Amount — prefer prefix form (EUR 1.234,56), fall back to suffix
    m = _RE_AMOUNT_PREFIX.search(text)
    if not m:
        m = _RE_AMOUNT_SUFFIX.search(text)
    if m:
        fields["amount_eur"] = _normalize_amount(m.group(1))

    # Invoice number
    m = _RE_INVOICE_NUMBER.search(text)
    if m:
        fields["invoice_number"] = m.group(1).strip()

    # Due date
    m = _RE_DUE_DATE.search(text)
    if m:
        fields["due_date"] = m.group(1).strip()

    # Invoice date
    m = _RE_INVOICE_DATE.search(text)
    if m:
        fields["invoice_date"] = m.group(1).strip()

    # BIC — only if IBAN found nearby; just pick first plausible BIC
    if fields["iban"]:
        m = _RE_BIC.search(text)
        if m:
            candidate = m.group(1)
            # Avoid mistaking the IBAN itself for a BIC
            if candidate not in (fields["iban"] or ""):
                fields["bic"] = candidate

    return fields


def compute_confidence(fields: dict) -> float:
    """Score 0.0–1.0 based on how many key fields were found."""
    score = 0.0
    if fields.get("amount_eur") is not None:
        score += 0.30
    if fields.get("iban"):
        score += 0.25
    if fields.get("invoice_number"):
        score += 0.20
    if fields.get("due_date"):
        score += 0.15
    if fields.get("vendor"):
        score += 0.10
    return round(score, 4)


def _read_text_from_pdf(pdf_path: Path) -> str:
    """Extract all text from a PDF, handling encoding errors gracefully."""
    lines = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines.append(text)
    return "\n".join(lines)


def extract_from_pdf(pdf_path: Path) -> dict:
    """
    Extract invoice fields from a PDF using pdfplumber + regex.
    Falls back to extraction_method='llm_fallback' if confidence < 0.4.
    """
    try:
        text = _read_text_from_pdf(pdf_path)
    except Exception:
        # Try reading bytes and decoding with latin-1 as last resort
        try:
            raw = pdf_path.read_bytes()
            text = raw.decode("latin-1", errors="replace")
        except Exception:
            text = ""

    fields = _extract_fields_from_text(text)

    # Attempt vendor heuristic: first non-empty line of first page
    first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), None)
    if first_line and not fields["vendor"]:
        fields["vendor"] = first_line[:80]

    confidence = compute_confidence(fields)
    if confidence < 0.4:
        extraction_method = "llm_fallback"
    else:
        extraction_method = "regex"

    return {
        **fields,
        "confidence": confidence,
        "extraction_method": extraction_method,
    }


def extract_from_html(html: str) -> dict:
    """
    Extract invoice fields from HTML email body using BeautifulSoup + regex.
    Same return format as extract_from_pdf.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
    except Exception:
        text = html  # Fallback: treat raw html as text

    fields = _extract_fields_from_text(text)

    # Vendor heuristic: <title> tag or first heading
    vendor = None
    title_tag = soup.find("title") if "soup" in dir() else None
    if title_tag and title_tag.get_text(strip=True):
        vendor = title_tag.get_text(strip=True)[:80]
    if not vendor:
        for tag in ("h1", "h2", "h3"):
            heading = soup.find(tag) if "soup" in dir() else None
            if heading and heading.get_text(strip=True):
                vendor = heading.get_text(strip=True)[:80]
                break
    if vendor and not fields["vendor"]:
        fields["vendor"] = vendor

    confidence = compute_confidence(fields)
    extraction_method = "regex" if confidence >= 0.4 else "llm_fallback"

    return {
        **fields,
        "confidence": confidence,
        "extraction_method": extraction_method,
    }


def _stable_id(source: str, invoice_number: str | None, text_hash: str) -> str:
    content = f"{source}|{invoice_number or ''}|{text_hash}"
    return hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()[:16]


def main() -> None:
    """CLI: uv run scripts/extract_invoice.py <pdf_path> [--data-dir PATH]"""
    parser = argparse.ArgumentParser(description="Extract invoice fields from a PDF.")
    parser.add_argument("pdf_path", type=Path, help="Path to the PDF file")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Finance data directory")
    args = parser.parse_args()

    pdf_path: Path = args.pdf_path
    data_dir: Path = args.data_dir

    if not pdf_path.exists():
        print(f"Error: file not found: {pdf_path}")
        raise SystemExit(1)

    result = extract_from_pdf(pdf_path)

    # Compute stable ID
    raw_bytes = pdf_path.read_bytes()
    content_hash = hashlib.sha256(raw_bytes).hexdigest()[:16]
    invoice_id = _stable_id(str(pdf_path), result.get("invoice_number"), content_hash)

    extracted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    row = {
        "id": invoice_id,
        "email_id": None,
        "extracted_at": extracted_at,
        "source_type": "pdf_attachment",
        "extraction_method": result["extraction_method"],
        "vendor": result.get("vendor"),
        "invoice_number": result.get("invoice_number"),
        "invoice_date": result.get("invoice_date"),
        "due_date": result.get("due_date"),
        "amount_eur": result.get("amount_eur"),
        "iban": result.get("iban"),
        "bic": result.get("bic"),
        "description": result.get("description"),
        "raw_path": str(pdf_path),
        "confidence": result["confidence"],
        "notes": None,
    }

    conn = db.get_db(data_dir)
    db.upsert(conn, "invoices", row)
    conn.close()

    audit.log(
        data_dir,
        action="invoice_extracted",
        entity_type="invoice",
        entity_id=invoice_id,
        details={
            "source": str(pdf_path),
            "extraction_method": result["extraction_method"],
            "confidence": result["confidence"],
            "invoice_number": result.get("invoice_number"),
            "amount_eur": result.get("amount_eur"),
            "iban": result.get("iban"),
        },
    )

    print(f"Invoice ID : {invoice_id}")
    print(f"Method     : {result['extraction_method']}")
    print(f"Confidence : {result['confidence']:.2f}")
    for key in ("vendor", "invoice_number", "invoice_date", "due_date", "amount_eur", "iban", "bic"):
        print(f"{key:<20}: {result.get(key)}")


if __name__ == "__main__":
    main()
