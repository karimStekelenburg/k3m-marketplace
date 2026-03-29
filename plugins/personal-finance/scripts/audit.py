"""Append-only JSONL audit log for personal-finance plugin."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def log(
    data_dir: Path,
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict,
) -> None:
    """Append one line to audit.jsonl with timestamp, action, entity info, and details."""
    data_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": details,
    }
    audit_path = data_dir / "audit.jsonl"
    with audit_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
