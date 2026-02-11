"""
merge_csv.py
Fetches today's CSV from the colleague's private repo and merges it
into data/app-home-merged.csv, deduplicating rows.

Required env vars:
  SOURCE_REPO   – e.g. "myorg/scraper-repo"
  SOURCE_PATH   – folder in that repo, e.g. "output"
  GH_PAT        – GitHub Personal Access Token with repo scope
"""

import os
import sys
import csv
import io
import base64
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json

MERGED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "app-home-merged.csv")
HEADER = ["Date and time of publication", "article", "hyperlink", "code", "slot"]


def github_api(url, token):
    req = Request(url)
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())


def fetch_csv_content(repo, path, filename, token):
    """Fetch a single file's content from a private repo via the GitHub API."""
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}/{filename}"
    try:
        data = github_api(api_url, token)
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content
    except HTTPError as e:
        if e.code == 404:
            return None
        raise


def list_csv_files(repo, path, token):
    """List all CSV files in the source folder."""
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    try:
        data = github_api(api_url, token)
        return [f["name"] for f in data if f["name"].endswith(".csv")]
    except HTTPError:
        return []


def parse_csv_rows(text):
    """Parse CSV text into list of row tuples (for deduplication)."""
    rows = set()
    reader = csv.reader(io.StringIO(text))
    for row in reader:
        if len(row) >= 5:
            # skip if it looks like a header
            if row[0].strip().lower().startswith("date"):
                continue
            cleaned = tuple(c.strip() for c in row[:5])
            rows.add(cleaned)
    return rows


def load_existing():
    """Load existing merged CSV rows."""
    if not os.path.exists(MERGED_PATH):
        return set()
    with open(MERGED_PATH, "r", newline="") as f:
        return parse_csv_rows(f.read())


def save_merged(rows):
    """Write all rows to merged CSV with header."""
    sorted_rows = sorted(rows, key=lambda r: (r[0], int(r[4])))
    with open(MERGED_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for row in sorted_rows:
            writer.writerow(row)
    return len(sorted_rows)


def main():
    repo = os.environ.get("SOURCE_REPO")
    path = os.environ.get("SOURCE_PATH", "output")
    token = os.environ.get("GH_PAT")

    if not repo or not token:
        print("ERROR: SOURCE_REPO and GH_PAT environment variables are required.")
        sys.exit(1)

    print(f"Source: {repo}/{path}")

    # Load existing data
    existing = load_existing()
    print(f"Existing rows: {len(existing)}")

    # Try fetching today's and yesterday's CSV (in case the hour straddles midnight)
    today = datetime.utcnow()
    dates_to_try = [today, today - timedelta(days=1)]

    new_count = 0
    for d in dates_to_try:
        filename = f"app-home-{d.strftime('%Y-%m-%d')}.csv"
        print(f"Fetching {filename}...")
        content = fetch_csv_content(repo, path, filename, token)
        if content:
            new_rows = parse_csv_rows(content)
            added = new_rows - existing
            if added:
                print(f"  Found {len(added)} new rows in {filename}")
                existing |= added
                new_count += len(added)
            else:
                print(f"  No new rows in {filename}")
        else:
            print(f"  {filename} not found, skipping")

    if new_count > 0:
        total = save_merged(existing)
        print(f"Merged CSV updated: {total} total rows ({new_count} new)")
    else:
        print("No new data. Merged CSV unchanged.")


if __name__ == "__main__":
    main()
