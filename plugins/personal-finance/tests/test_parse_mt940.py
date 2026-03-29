"""Tests for scripts/parse_mt940.py."""

from scripts.parse_mt940 import parse_mt940_file  # type: ignore
from tests.conftest import FIXTURES_DIR

REQUIRED_FIELDS = {"id", "bank", "date", "amount_eur", "description"}


def test_parse_mt940_returns_transactions():
    txns = parse_mt940_file(FIXTURES_DIR / "sample.mt940", "abn_amro")
    assert isinstance(txns, list)
    assert len(txns) > 0


def test_mt940_transaction_has_required_fields():
    txns = parse_mt940_file(FIXTURES_DIR / "sample.mt940", "abn_amro")
    for txn in txns:
        for field in REQUIRED_FIELDS:
            assert field in txn, f"Missing field '{field}' in transaction"


def test_mt940_amounts_are_floats():
    txns = parse_mt940_file(FIXTURES_DIR / "sample.mt940", "abn_amro")
    for txn in txns:
        assert isinstance(txn["amount_eur"], float), f"amount_eur is not float: {txn['amount_eur']!r}"


def test_mt940_debit_is_negative():
    txns = parse_mt940_file(FIXTURES_DIR / "sample.mt940", "abn_amro")
    # sample.mt940 fixture has D (debit) transactions; they should be negative
    debit_txns = [t for t in txns if t["amount_eur"] < 0]
    assert len(debit_txns) > 0, "Expected at least one debit (negative) transaction"
    for txn in debit_txns:
        assert txn["amount_eur"] < 0


def test_mt940_credit_is_positive():
    txns = parse_mt940_file(FIXTURES_DIR / "sample.mt940", "abn_amro")
    # sample.mt940 fixture has C (credit) transaction on 2024-01-05
    credit_txns = [t for t in txns if t["amount_eur"] > 0]
    assert len(credit_txns) > 0, "Expected at least one credit (positive) transaction"
    for txn in credit_txns:
        assert txn["amount_eur"] > 0
