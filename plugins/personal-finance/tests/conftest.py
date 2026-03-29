import sys
from pathlib import Path

# Add plugin root to path so scripts can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def data_dir(tmp_path):
    """A fresh temporary data directory for each test."""
    d = tmp_path / "finance-data"
    d.mkdir()
    (d / "qr").mkdir()
    return d


@pytest.fixture
def db_conn(data_dir):
    """An initialized DB connection."""
    from scripts.db import get_db  # type: ignore
    return get_db(data_dir)


@pytest.fixture
def sample_invoice():
    return {
        "id": "test_invoice_001",
        "email_id": None,
        "extracted_at": "2026-01-15T10:00:00Z",
        "source_type": "pdf_attachment",
        "extraction_method": "regex",
        "vendor": "Accountantskantoor Jansen",
        "invoice_number": "2024-001",
        "invoice_date": "2024-01-10",
        "due_date": "2024-02-10",
        "amount_eur": 363.00,
        "iban": "NL91ABNA0417164300",
        "bic": "ABNANL2A",
        "description": "Factuur 2024-001 accountantskosten",
        "raw_path": None,
        "confidence": 0.9,
        "notes": None,
    }


@pytest.fixture
def sample_transaction():
    return {
        "id": "test_txn_001",
        "imported_at": "2026-01-20T10:00:00Z",
        "bank": "abn_amro",
        "source_file": "sample.csv",
        "date": "2024-01-15",
        "amount_eur": -363.00,
        "counterparty_name": "Accountantskantoor Jansen",
        "counterparty_iban": "NL91ABNA0417164300",
        "description": "Betaling factuur 2024-001",
        "raw_line": "raw data here",
    }
