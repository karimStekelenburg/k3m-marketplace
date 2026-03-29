"""Tests for scripts/extract_invoice.py — regex and confidence logic."""

from scripts.extract_invoice import compute_confidence, extract_from_html  # type: ignore


def test_compute_confidence_full():
    fields = {
        "amount_eur": 363.00,
        "iban": "NL91ABNA0417164300",
        "invoice_number": "2024-001",
        "due_date": "2024-02-10",
        "vendor": "Accountantskantoor Jansen",
    }
    confidence = compute_confidence(fields)
    assert confidence >= 0.9


def test_compute_confidence_partial():
    # Only amount_eur (0.30) + iban (0.25) = 0.55
    fields = {
        "amount_eur": 363.00,
        "iban": "NL91ABNA0417164300",
        "invoice_number": None,
        "due_date": None,
        "vendor": None,
    }
    confidence = compute_confidence(fields)
    assert abs(confidence - 0.55) < 0.01


def test_compute_confidence_empty():
    confidence = compute_confidence({})
    assert confidence == 0.0


def test_extract_from_html_finds_iban():
    html = """
    <html><body>
    <p>Bankrekening: NL91ABNA0417164300</p>
    <p>Bedrag: € 363,00</p>
    </body></html>
    """
    result = extract_from_html(html)
    assert result["iban"] == "NL91ABNA0417164300"


def test_extract_from_html_finds_amount():
    html = """
    <html><body>
    <p>Te betalen: € 363,00</p>
    <p>IBAN: NL91ABNA0417164300</p>
    </body></html>
    """
    result = extract_from_html(html)
    assert result["amount_eur"] is not None
    assert abs(result["amount_eur"] - 363.0) < 0.01


def test_extract_from_html_finds_invoice_number():
    # Use "Factuur: 2024-001" — the regex alternates match "factuur" and then
    # capture the value after the colon separator.
    html = """
    <html><body>
    <p>Factuur: 2024-001</p>
    <p>Bedrag: € 363,00</p>
    </body></html>
    """
    result = extract_from_html(html)
    assert result["invoice_number"] is not None
    assert "2024-001" in result["invoice_number"]
