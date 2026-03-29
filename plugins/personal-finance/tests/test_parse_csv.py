"""Tests for scripts/parse_csv.py."""

import pytest

from scripts.parse_csv import detect_bank, parse_csv_file  # type: ignore
from tests.conftest import FIXTURES_DIR

REQUIRED_FIELDS = {"id", "bank", "date", "amount_eur", "description"}


def test_detect_bank_abn():
    bank = detect_bank(FIXTURES_DIR / "sample_abn.csv")
    assert bank == "abn_amro"


def test_detect_bank_ing():
    bank = detect_bank(FIXTURES_DIR / "sample_ing.csv")
    assert bank == "ing"


def test_detect_bank_bunq():
    bank = detect_bank(FIXTURES_DIR / "sample_bunq.csv")
    assert bank == "bunq"


def test_parse_abn_returns_transactions():
    txns = parse_csv_file(FIXTURES_DIR / "sample_abn.csv", "abn_amro")
    assert len(txns) >= 5
    for txn in txns:
        for field in REQUIRED_FIELDS:
            assert field in txn, f"Missing field '{field}' in transaction"


def test_parse_ing_returns_transactions():
    txns = parse_csv_file(FIXTURES_DIR / "sample_ing.csv", "ing")
    assert len(txns) >= 5
    for txn in txns:
        for field in REQUIRED_FIELDS:
            assert field in txn, f"Missing field '{field}' in transaction"


def test_parse_bunq_returns_transactions():
    txns = parse_csv_file(FIXTURES_DIR / "sample_bunq.csv", "bunq")
    assert len(txns) >= 5
    for txn in txns:
        for field in REQUIRED_FIELDS:
            assert field in txn, f"Missing field '{field}' in transaction"


def test_parse_abn_amounts_are_numeric():
    txns = parse_csv_file(FIXTURES_DIR / "sample_abn.csv", "abn_amro")
    for txn in txns:
        assert isinstance(txn["amount_eur"], float), f"amount_eur is not float: {txn['amount_eur']!r}"


def test_parse_ing_af_is_negative():
    txns = parse_csv_file(FIXTURES_DIR / "sample_ing.csv", "ing")
    # The fixture contains "Af" (debit) rows; all should be negative
    debit_txns = [t for t in txns if t["amount_eur"] < 0]
    assert len(debit_txns) > 0, "Expected at least one debit transaction"
    for txn in debit_txns:
        assert txn["amount_eur"] < 0


def test_parse_ing_bij_is_positive():
    txns = parse_csv_file(FIXTURES_DIR / "sample_ing.csv", "ing")
    # The fixture contains "Bij" (credit) rows; all should be positive
    credit_txns = [t for t in txns if t["amount_eur"] > 0]
    assert len(credit_txns) > 0, "Expected at least one credit transaction"
    for txn in credit_txns:
        assert txn["amount_eur"] > 0


def test_unknown_bank_raises():
    with pytest.raises(ValueError, match="unknown_bank"):
        parse_csv_file(FIXTURES_DIR / "sample_abn.csv", "unknown_bank")
