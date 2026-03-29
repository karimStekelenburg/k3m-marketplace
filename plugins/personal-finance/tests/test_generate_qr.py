"""Tests for scripts/generate_qr.py."""

import pytest

from scripts.generate_qr import generate_epc_qr  # type: ignore


def test_generate_epc_qr_creates_file(sample_invoice, tmp_path):
    out_path = generate_epc_qr(sample_invoice, tmp_path)
    assert out_path.exists()


def test_generate_epc_qr_filename(sample_invoice, tmp_path):
    out_path = generate_epc_qr(sample_invoice, tmp_path)
    assert out_path.name == "qr_test_invoice_001.png"


def test_generate_epc_qr_no_iban_raises(sample_invoice, tmp_path):
    invoice = dict(sample_invoice, iban=None)
    with pytest.raises(ValueError):
        generate_epc_qr(invoice, tmp_path)


def test_generate_epc_qr_zero_amount_raises(sample_invoice, tmp_path):
    invoice = dict(sample_invoice, amount_eur=0)
    with pytest.raises(ValueError):
        generate_epc_qr(invoice, tmp_path)
