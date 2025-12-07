from __future__ import annotations

from pathlib import Path
from typing import List
import re

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs" / "theory.md"
PDF_PATH = ROOT / "docs" / "theory.pdf"


def escape(text: str) -> str:
    """Escapes characters that ReportLab treats as XML."""

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def format_inline_markup(text: str) -> str:
    """Apply simple markdown-style replacements for bold and inline code."""

    def repl_bold(match: re.Match[str]) -> str:
        return f"<b>{match.group(1)}</b>"

    def repl_code(match: re.Match[str]) -> str:
        return f"<font face='Courier'>{match.group(1)}</font>"

    formatted = re.sub(r"\*\*(.+?)\*\*", repl_bold, text)
    formatted = re.sub(r"`(.+?)`", repl_code, formatted)
    return formatted


def parse_markdown(lines: List[str]) -> List:
    """Very small subset of Markdown tailored to the theory notes."""

    styles = getSampleStyleSheet()
    heading1 = ParagraphStyle(
        "Heading1Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        spaceAfter=6,
    )
    heading2 = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
    )
    code = ParagraphStyle(
        "CodeCustom",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=9.5,
        leading=12,
    )

    story: List = []
    in_code_block = False
    code_buffer: List[str] = []

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        if line.strip().startswith("```"):
            if in_code_block:
                story.append(Preformatted("\n".join(code_buffer), code))
                story.append(Spacer(1, 0.1 * inch))
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 0.12 * inch))
            continue

        if stripped == "---":
            story.append(Spacer(1, 0.18 * inch))
            continue

        if stripped.startswith("# "):
            text = escape(stripped[2:].strip())
            story.append(Paragraph(text, heading1))
            story.append(Spacer(1, 0.08 * inch))
            continue

        if stripped.startswith("## "):
            text = escape(stripped[3:].strip())
            story.append(Paragraph(text, heading2))
            story.append(Spacer(1, 0.05 * inch))
            continue

        paragraph_text = escape(line)
        paragraph_text = format_inline_markup(paragraph_text)
        story.append(Paragraph(paragraph_text, body))

    if code_buffer:
        story.append(Preformatted("\n".join(code_buffer), code))

    return story


def build_pdf() -> None:
    if not MD_PATH.exists():
        raise FileNotFoundError(f"Missing source markdown at {MD_PATH}")

    lines = MD_PATH.read_text().splitlines()
    story = parse_markdown(lines)

    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=LETTER, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    doc.build(story)


if __name__ == "__main__":
    build_pdf()
