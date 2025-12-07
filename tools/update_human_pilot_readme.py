#!/usr/bin/env python3
"""Update `data/human_pilot/README.md` with the current participant count.

Replaces the section between <!-- PILOT_COUNT:START --> and <!-- PILOT_COUNT:END -->
with a one-line summary containing the current count and UTC timestamp.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "human_pilot" / "pilot_ratings.csv"
README_PATH = ROOT / "data" / "human_pilot" / "README.md"


def count_responses(csv_path: Path) -> int:
    if not csv_path.exists():
        return 0
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    # subtract header if present
    if len(rows) == 0:
        return 0
    return max(0, len(rows) - 1)


def update_readme(readme_path: Path, count: int) -> None:
    text = readme_path.read_text(encoding="utf-8")
    start_tag = "<!-- PILOT_COUNT:START -->"
    end_tag = "<!-- PILOT_COUNT:END -->"
    if start_tag not in text or end_tag not in text:
        print("README missing pilot count markers; aborting.")
        sys.exit(1)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    new_block = f"{start_tag}\nParticipant count: the current pilot snapshot contains **{count}** responses (last updated: {timestamp}).\n{end_tag}"

    pre, rest = text.split(start_tag, 1)
    _, post = rest.split(end_tag, 1)
    new_text = pre + new_block + post
    readme_path.write_text(new_text, encoding="utf-8")
    print(f"Updated {readme_path} with count={count} at {timestamp}")


def main():
    count = count_responses(CSV_PATH)
    update_readme(README_PATH, count)


if __name__ == "__main__":
    main()
