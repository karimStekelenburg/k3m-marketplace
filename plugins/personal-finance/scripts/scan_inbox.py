"""Scan Apple Mail for invoice-related emails via AppleScript."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scripts import audit, db

DATA_DIR = Path.home() / "Documents" / "finance-data"

SEARCH_TERMS = [
    "factuur",
    "invoice",
    "rekening",
    "nota",
    "payment due",
    "te betalen",
    "betalingsherinnering",
    "herinnering",
]


def _build_applescript(days_back: int) -> str:
    """Return an AppleScript that queries all mailboxes for matching emails."""
    # Build a comma-separated quoted list of search terms for AppleScript
    terms_as = ", ".join(f'"{t}"' for t in SEARCH_TERMS)
    return f"""
set searchTerms to {{{terms_as}}}
set cutoffDate to (current date) - ({days_back} * days)
set results to {{}}

tell application "Mail"
    set allAccounts to every account
    repeat with acct in allAccounts
        set allMailboxes to every mailbox of acct
        repeat with mbox in allMailboxes
            set msgs to (messages of mbox whose date received >= cutoffDate)
            repeat with msg in msgs
                set msgSubject to subject of msg
                set msgSender to sender of msg
                set matched to false
                repeat with term in searchTerms
                    if (msgSubject contains term) or (msgSender contains term) then
                        set matched to true
                        exit repeat
                    end if
                end repeat
                if matched then
                    set msgId to message id of msg
                    set msgDate to date received of msg as string
                    set attNames to {{}}
                    set attList to mail attachments of msg
                    repeat with att in attList
                        set end of attNames to name of att
                    end repeat
                    set hasAtt to (count of attNames) > 0
                    set bodyText to ""
                    try
                        set fullBody to content of msg
                        if (count of fullBody) > 500 then
                            set bodyText to text 1 thru 500 of fullBody
                        else
                            set bodyText to fullBody
                        end if
                    end try
                    -- Encode as tab-delimited record separator "|RECORD|"
                    set attNamesStr to ""
                    repeat with i from 1 to count of attNames
                        if i > 1 then set attNamesStr to attNamesStr & "|||"
                        set attNamesStr to attNamesStr & (item i of attNames)
                    end repeat
                    set record to msgId & "\\t" & msgSubject & "\\t" & msgSender & "\\t" & msgDate & "\\t" & (hasAtt as string) & "\\t" & attNamesStr & "\\t" & bodyText
                    set end of results to record
                end if
            end repeat
        end repeat
    end repeat
end tell

set output to ""
repeat with i from 1 to count of results
    if i > 1 then set output to output & "|RECORD|"
    set output to output & (item i of results)
end repeat
return output
"""


def _parse_applescript_output(raw: str) -> list[dict]:
    """Parse the tab/record-delimited AppleScript output into a list of dicts."""
    if not raw.strip():
        return []
    emails = []
    for record in raw.split("|RECORD|"):
        record = record.strip()
        if not record:
            continue
        parts = record.split("\t", 6)
        if len(parts) < 7:
            # Pad missing fields
            parts += [""] * (7 - len(parts))
        msg_id, subject, sender, date_str, has_att_str, att_names_str, body = parts
        has_att = has_att_str.lower() == "true"
        attachment_names = [n for n in att_names_str.split("|||") if n] if att_names_str else []
        emails.append(
            {
                "msg_id": msg_id.strip(),
                "subject": subject.strip(),
                "sender": sender.strip(),
                "date": date_str.strip(),
                "has_attachment": has_att,
                "attachment_names": attachment_names,
                "body_snippet": body.strip(),
            }
        )
    return emails


def _stable_id(msg_id: str, subject: str) -> str:
    content = f"{msg_id}|{subject}"
    return hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()[:16]


def scan_inbox(data_dir: Path = DATA_DIR, days_back: int = 90) -> list[dict]:
    """
    Query Apple Mail via AppleScript for emails matching invoice keywords.
    Returns list of dicts with: id, subject, sender, date, has_attachment,
    attachment_names, body_snippet.
    Writes results to DB and audit log.
    """
    script = _build_applescript(days_back)
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript failed: {result.stderr.strip()}")

    raw_output = result.stdout
    parsed = _parse_applescript_output(raw_output)

    conn = db.get_db(data_dir)
    scanned_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    output = []
    for email in parsed:
        email_id = _stable_id(email["msg_id"], email["subject"])
        row = {
            "id": email_id,
            "scanned_at": scanned_at,
            "subject": email["subject"],
            "sender": email["sender"],
            "date": email["date"],
            "has_attachment": 1 if email["has_attachment"] else 0,
            "attachment_names": json.dumps(email["attachment_names"], ensure_ascii=False),
            "body_snippet": email["body_snippet"],
            "raw_path": None,
            "status": "pending",
        }
        db.upsert(conn, "emails", row)
        audit.log(
            data_dir,
            action="email_scanned",
            entity_type="email",
            entity_id=email_id,
            details={
                "subject": email["subject"],
                "sender": email["sender"],
                "date": email["date"],
                "has_attachment": email["has_attachment"],
            },
        )
        output.append(
            {
                "id": email_id,
                "subject": email["subject"],
                "sender": email["sender"],
                "date": email["date"],
                "has_attachment": email["has_attachment"],
                "attachment_names": email["attachment_names"],
                "body_snippet": email["body_snippet"],
            }
        )
    conn.close()
    return output


def main() -> None:
    """CLI entry point: uv run scripts/scan_inbox.py [--days 90] [--data-dir PATH]"""
    parser = argparse.ArgumentParser(description="Scan Apple Mail for invoice emails.")
    parser.add_argument("--days", type=int, default=90, help="Number of days back to search (default: 90)")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Finance data directory")
    args = parser.parse_args()

    emails = scan_inbox(data_dir=args.data_dir, days_back=args.days)
    print(f"Found {len(emails)} matching email(s).")
    for e in emails:
        att = ", ".join(e["attachment_names"]) if e["attachment_names"] else "none"
        print(f"  [{e['id']}] {e['date']} | {e['sender']} | {e['subject']} | attachments: {att}")


if __name__ == "__main__":
    main()
