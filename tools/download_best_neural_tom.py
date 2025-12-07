#!/usr/bin/env python3
"""Utility to fetch the best_neural_tom checkpoint from remote storage."""
from __future__ import annotations

import argparse
import os
import pathlib
import sys
import urllib.request

DEFAULT_DEST = pathlib.Path("best_neural_tom.pth")
ENV_VAR = "BEST_NEURAL_TOM_URL"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download the best_neural_tom.pth checkpoint from a Release or Hugging Face Hub. "
            "Pass --url explicitly or set the BEST_NEURAL_TOM_URL environment variable."
        )
    )
    parser.add_argument(
        "--url",
        help="Direct download URL for the checkpoint (Release asset, HF Hub file, etc.)",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=DEFAULT_DEST,
        help=f"Destination path for the checkpoint (default: {DEFAULT_DEST})",
    )
    return parser.parse_args()


def resolve_url(cli_url: str | None) -> str:
    url = cli_url or os.environ.get(ENV_VAR)
    if not url:
        raise SystemExit(
            "No download URL provided. Supply --url or set the BEST_NEURAL_TOM_URL environment variable."
        )
    return url


def download_checkpoint(url: str, dest: pathlib.Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, open(dest, "wb") as target:
        target.write(response.read())


def main() -> None:
    args = parse_args()
    url = resolve_url(args.url)
    print(f"Downloading checkpoint from {url} ...")
    download_checkpoint(url, args.output)
    print(f"Saved checkpoint to {args.output.resolve()}")


if __name__ == "__main__":
    main()
