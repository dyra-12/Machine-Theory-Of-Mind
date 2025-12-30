#!/usr/bin/env python3
"""Export tables and figures referenced in docs/Results.md into docs/figures/.

Goal
- Do NOT regenerate experiments or overwrite artifacts in results/.
- Only read existing files (e.g., results/week*/plots/*.png) and copy/emit
  documentation assets under docs/figures/.

What it does
- Copies every local Markdown image referenced in the provided Results.md into
  the output directory.
- Extracts every Markdown table that follows a "#### Table" heading and writes
  it as a standalone markdown file (table_XX_*.md) under the output directory.
- Writes an index markdown file listing exported assets.

This is intended to support a one-command "docs assets" build for paper/docs.
"""

from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]


IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
TABLE_HEADING_RE = re.compile(r"^####\s+Table\s+(\d+)\.?\s*(.*)$")


@dataclass(frozen=True)
class ExportedAsset:
    kind: str  # "figure" | "table" | "index"
    src: Optional[Path]
    dst: Path


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "untitled"


def _iter_image_links(md_text: str) -> Iterable[str]:
    for match in IMAGE_RE.finditer(md_text):
        yield match.group(1).strip()


def _is_local_path(link: str) -> bool:
    lowered = link.lower()
    if lowered.startswith("http://") or lowered.startswith("https://"):
        return False
    if lowered.startswith("data:"):
        return False
    return True


def _safe_dest_name(src: Path) -> str:
    # Keep filenames stable and collision-resistant across results/week*/plots.
    parts = list(src.parts)
    try:
        idx = parts.index("results")
        rel = Path(*parts[idx + 1 :])
        prefix = "_".join(rel.parts[:-1])
        if prefix:
            return f"{prefix}_{src.name}"
    except ValueError:
        pass
    return src.name


def export_images(results_md: Path, out_dir: Path, overwrite: bool) -> List[ExportedAsset]:
    text = results_md.read_text(encoding="utf-8")
    assets: List[ExportedAsset] = []

    for raw_link in _iter_image_links(text):
        if " " in raw_link:
            # Markdown allows spaces if escaped; keep simple: treat as-is.
            link = raw_link
        else:
            link = raw_link

        if not _is_local_path(link):
            continue

        src = (results_md.parent / link).resolve()
        if not src.exists():
            # Skip missing assets, but keep going.
            continue

        dest_name = _safe_dest_name(src)
        dst = out_dir / dest_name

        if dst.exists() and not overwrite:
            assets.append(ExportedAsset(kind="figure", src=src, dst=dst))
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        assets.append(ExportedAsset(kind="figure", src=src, dst=dst))

    return assets


def _extract_table_block(lines: List[str], start_idx: int) -> Tuple[List[str], int]:
    """Extract a markdown pipe table starting at first '|' line.

    Returns (table_lines, next_index_after_table).
    """
    table_lines: List[str] = []
    i = start_idx

    # Must start with a table row
    if i >= len(lines) or not lines[i].lstrip().startswith("|"):
        return table_lines, start_idx

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            break
        if not line.lstrip().startswith("|"):
            break
        table_lines.append(line.rstrip("\n"))
        i += 1

    return table_lines, i


def export_tables(results_md: Path, out_dir: Path, overwrite: bool) -> List[ExportedAsset]:
    text = results_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    assets: List[ExportedAsset] = []

    i = 0
    while i < len(lines):
        heading_match = TABLE_HEADING_RE.match(lines[i])
        if not heading_match:
            i += 1
            continue

        table_num = heading_match.group(1)
        title = heading_match.group(2) or ""
        slug = _slugify(title)[:60]

        # Look ahead for the first pipe-table block (skip blank lines, source notes, etc.)
        j = i + 1
        while j < len(lines) and not lines[j].lstrip().startswith("|"):
            j += 1

        table_lines, next_idx = _extract_table_block(lines, j)
        if not table_lines:
            i += 1
            continue

        filename = f"table_{int(table_num):02d}_{slug}.md" if slug else f"table_{int(table_num):02d}.md"
        dst = out_dir / filename

        if dst.exists() and not overwrite:
            assets.append(ExportedAsset(kind="table", src=results_md, dst=dst))
            i = next_idx
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        content = "\n".join([
            f"#### Table {table_num}. {title}".rstrip(),
            "",
            *table_lines,
            "",
        ])
        dst.write_text(content, encoding="utf-8")
        assets.append(ExportedAsset(kind="table", src=results_md, dst=dst))
        i = next_idx

    return assets


def write_index(out_dir: Path, results_md: Path, assets: List[ExportedAsset]) -> ExportedAsset:
    index_path = out_dir / "index.md"

    figures = [a for a in assets if a.kind == "figure"]
    tables = [a for a in assets if a.kind == "table"]

    def rel(p: Path) -> str:
        return p.relative_to(ROOT).as_posix()

    lines: List[str] = []
    lines.append("# Exported Results Assets")
    lines.append("")
    lines.append(f"Source: `{results_md.relative_to(ROOT).as_posix()}`")
    lines.append("")

    if figures:
        lines.append("## Figures")
        lines.append("")
        for a in figures:
            lines.append(f"- `{rel(a.dst)}` (from `{rel(a.src)}`)")
        lines.append("")

    if tables:
        lines.append("## Tables")
        lines.append("")
        for a in tables:
            lines.append(f"- `{rel(a.dst)}`")
        lines.append("")

    out_dir.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return ExportedAsset(kind="index", src=results_md, dst=index_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-md",
        type=Path,
        default=ROOT / "docs" / "Results.md",
        help="Path to docs/Results.md",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "docs" / "figures",
        help="Output directory (default: docs/figures)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in out-dir",
    )

    args = parser.parse_args()
    results_md = args.results_md.resolve()
    out_dir = args.out_dir.resolve()

    if not results_md.exists():
        raise FileNotFoundError(f"Missing Results.md: {results_md}")

    exported: List[ExportedAsset] = []
    exported.extend(export_images(results_md=results_md, out_dir=out_dir, overwrite=args.overwrite))
    exported.extend(export_tables(results_md=results_md, out_dir=out_dir, overwrite=args.overwrite))
    index_asset = write_index(out_dir=out_dir, results_md=results_md, assets=exported)

    print(f"Exported {len([a for a in exported if a.kind == 'figure'])} figure files")
    print(f"Exported {len([a for a in exported if a.kind == 'table'])} table files")
    print(f"Wrote index: {index_asset.dst}")
    print("Note: This command does not modify anything under results/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
