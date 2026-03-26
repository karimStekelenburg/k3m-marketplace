#!/usr/bin/env python3
"""Fetch all resources from resources.json and cache locally.

Usage:
    uv run scripts/fetch-resources.py [--data-dir DATA_DIR] [--cache-dir CACHE_DIR] [--category CATEGORY] [--id ID]

Reads resources.json, fetches each active URL, and stores the content
in a cache directory as individual files named by resource ID.
Produces a fetch-report.json summarizing results.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def fetch_url(url: str, timeout: int = 30) -> tuple[int, str, str]:
    """Fetch a URL using curl. Returns (status_code, content, error)."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", str(timeout), "-w", "\n%{http_code}", url],
            capture_output=True,
            text=True,
            timeout=timeout + 5,
        )
        lines = result.stdout.rsplit("\n", 1)
        if len(lines) == 2:
            content, status = lines
            return int(status), content, ""
        return 0, "", result.stderr or "Unknown error"
    except subprocess.TimeoutExpired:
        return 0, "", "Timeout"
    except Exception as e:
        return 0, "", str(e)


def main():
    parser = argparse.ArgumentParser(description="Fetch resources from resources.json")
    parser.add_argument("--data-dir", default=None, help="Directory containing resources.json")
    parser.add_argument("--cache-dir", default=None, help="Directory to store cached content")
    parser.add_argument("--category", default=None, help="Only fetch resources in this category")
    parser.add_argument("--id", default=None, help="Only fetch a specific resource by ID")
    parser.add_argument("--timeout", type=int, default=30, help="Per-request timeout in seconds")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    plugin_dir = script_dir.parent
    data_dir = Path(args.data_dir) if args.data_dir else plugin_dir / "data"
    cache_dir = Path(args.cache_dir) if args.cache_dir else data_dir / "cache"

    resources_path = data_dir / "resources.json"
    if not resources_path.exists():
        print(f"Error: {resources_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(resources_path) as f:
        data = json.load(f)

    cache_dir.mkdir(parents=True, exist_ok=True)

    resources = data.get("resources", [])
    if args.id:
        resources = [r for r in resources if r["id"] == args.id]
    if args.category:
        resources = [r for r in resources if r.get("category") == args.category]

    resources = [r for r in resources if r.get("status") == "active"]

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(resources),
        "success": 0,
        "failed": 0,
        "results": [],
    }

    for res in resources:
        rid = res["id"]
        url = res["url"]
        print(f"Fetching {rid}: {url} ...", end=" ")

        status, content, error = fetch_url(url, args.timeout)
        cache_file = cache_dir / f"{rid}.txt"

        entry = {"id": rid, "url": url, "status_code": status}

        if status >= 200 and status < 400 and content:
            cache_file.write_text(content)
            entry["cached"] = str(cache_file)
            entry["size"] = len(content)
            report["success"] += 1
            print(f"OK ({status}, {len(content)} bytes)")
        else:
            entry["error"] = error or f"HTTP {status}"
            report["failed"] += 1
            print(f"FAILED ({error or status})")

        report["results"].append(entry)

    report_path = data_dir / "fetch-report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nDone: {report['success']}/{report['total']} fetched, {report['failed']} failed")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
