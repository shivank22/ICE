#!/usr/bin/env python3
"""Assemble the Vanilla Agentic Framework blueprint guide PDF.

Extended from the product-overview-pdf skill builder with:
  - title page (title, subtitle, author, date)
  - table of contents with real page numbers (multiBuild)
  - table rendering ({"table": {...}} body items)
  - inline image embedding ({"image": {...}} body items) for all diagrams

Usage:
    python3 build_pdf.py --content content.json --output guide.pdf
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import (
        BaseDocTemplate,
        Frame,
        HRFlowable,
        Image,
        KeepTogether,
        ListFlowable,
        ListItem,
        PageBreak,
        PageTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.platypus.tableofcontents import TableOfContents
except ImportError:
    sys.exit("Missing dependency. Install with: pip3 install reportlab")

ACCENT = colors.HexColor("#2563EB")
DARK = colors.HexColor("#0F172A")
MUTED = colors.HexColor("#475569")
LIGHT_LINE = colors.HexColor("#E2E8F0")
TABLE_HEADER_BG = colors.HexColor("#1E3A8A")
TABLE_ALT_BG = colors.HexColor("#F1F5F9")


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "CoverTitle", parent=styles["Title"], fontSize=30, leading=36,
        textColor=DARK, alignment=TA_CENTER, spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        "CoverSubtitle", parent=styles["Normal"], fontSize=14, leading=20,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "CoverMeta", parent=styles["Normal"], fontSize=11, leading=16,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "SectionHeading", parent=styles["Heading1"], fontSize=17, leading=21,
        textColor=ACCENT, spaceBefore=16, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "BodyTextX", parent=styles["BodyText"], fontSize=10.5, leading=15.5,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "BulletX", parent=styles["BodyText"], fontSize=10.5, leading=15.5,
        textColor=DARK, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        "Caption", parent=styles["Normal"], fontSize=9, leading=12,
        textColor=MUTED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        "TableCell", parent=styles["Normal"], fontSize=8.5, leading=11.5,
        textColor=DARK,
    ))
    styles.add(ParagraphStyle(
        "TableHeader", parent=styles["Normal"], fontSize=8.5, leading=11.5,
        textColor=colors.white, fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        "TOCHeading", parent=styles["Heading1"], fontSize=17, leading=21,
        textColor=ACCENT, spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        "TOCEntry", parent=styles["Normal"], fontSize=11, leading=18,
        textColor=DARK, leftIndent=4,
    ))
    return styles


def scaled_image(path, max_width, max_height=17 * cm):
    reader = ImageReader(path)
    iw, ih = reader.getSize()
    ratio = min(max_width / iw, max_height / ih, 1.0)
    return Image(path, width=iw * ratio, height=ih * ratio)


def make_table(spec, styles, content_width):
    headers = spec.get("headers", [])
    rows = spec.get("rows", [])
    ncols = max(len(headers), *(len(r) for r in rows)) if rows else len(headers)

    data = [[Paragraph(str(h), styles["TableHeader"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles["TableCell"]) for c in row])

    col_width = content_width / ncols
    table = Table(data, colWidths=[col_width] * ncols, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LIGHT_LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT_BG))
    table.setStyle(TableStyle(style))

    flow = [Spacer(1, 0.15 * cm), table]
    if spec.get("caption"):
        flow.append(Paragraph(spec["caption"], styles["Caption"]))
    else:
        flow.append(Spacer(1, 0.3 * cm))
    return flow


def body_to_flowables(body, styles, content_width, base_dir):
    flow = []
    bullets = []

    def flush_bullets():
        if bullets:
            flow.append(ListFlowable(
                [ListItem(Paragraph(b, styles["BulletX"]), leftIndent=10)
                 for b in bullets],
                bulletType="bullet", bulletColor=ACCENT, bulletFontSize=8,
                leftIndent=12, spaceAfter=8,
            ))
            bullets.clear()

    for item in body:
        if isinstance(item, dict) and "table" in item:
            flush_bullets()
            flow.extend(make_table(item["table"], styles, content_width))
        elif isinstance(item, dict) and "image" in item:
            flush_bullets()
            spec = item["image"]
            path = (base_dir / spec["path"]).resolve()
            if not path.exists():
                print(f"Warning: image not found: {path}", file=sys.stderr)
                continue
            img_flow = [Spacer(1, 0.2 * cm), scaled_image(str(path), content_width)]
            if spec.get("caption"):
                img_flow.append(Paragraph(spec["caption"], styles["Caption"]))
            flow.append(KeepTogether(img_flow))
        else:
            text = str(item)
            if text.strip().startswith("- "):
                bullets.append(text.strip()[2:].strip())
            else:
                flush_bullets()
                flow.append(Paragraph(text, styles["BodyTextX"]))
    flush_bullets()
    return flow


class GuideDocTemplate(BaseDocTemplate):
    """Doc template that notifies the TOC when a section heading is placed."""

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "SectionHeading":
            text = flowable.getPlainText()
            self.notify("TOCEntry", (0, text, self.page))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True)
    ap.add_argument("--output", default="guide.pdf")
    args = ap.parse_args()

    content_path = Path(args.content)
    base_dir = content_path.parent
    content = json.loads(content_path.read_text())

    styles = build_styles()
    doc = GuideDocTemplate(
        args.output, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=content.get("title", "Guide"),
        author=content.get("author", ""),
    )
    content_width = doc.width

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        label = content.get("footer", "")
        if label and doc_.page > 1:
            canvas.drawString(2 * cm, 1.2 * cm, label)
        if doc_.page > 1:
            canvas.drawRightString(doc_.pagesize[0] - 2 * cm, 1.2 * cm,
                                   f"Page {doc_.page}")
        canvas.restoreState()

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])

    story = []

    # --- Title page ---
    story.append(Spacer(1, 5.5 * cm))
    story.append(Paragraph(content.get("title", "Guide"), styles["CoverTitle"]))
    if content.get("subtitle"):
        story.append(Paragraph(content["subtitle"], styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="40%", thickness=2, color=ACCENT,
                            hAlign="CENTER", spaceBefore=8, spaceAfter=14))
    if content.get("author"):
        story.append(Paragraph(f"Author: {content['author']}", styles["CoverMeta"]))
    if content.get("date"):
        story.append(Paragraph(content["date"], styles["CoverMeta"]))
    story.append(PageBreak())

    # --- Table of contents (index) ---
    story.append(Paragraph("Index", styles["TOCHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.6, color=LIGHT_LINE,
                            spaceBefore=0, spaceAfter=10))
    toc = TableOfContents()
    toc.levelStyles = [styles["TOCEntry"]]
    story.append(toc)
    story.append(PageBreak())

    # --- Sections ---
    sections = content.get("sections", [])
    for i, section in enumerate(sections):
        heading = section.get("heading", "")
        story.append(Paragraph(heading, styles["SectionHeading"]))
        story.append(HRFlowable(width="100%", thickness=0.6, color=LIGHT_LINE,
                                spaceBefore=0, spaceAfter=10))
        story.extend(body_to_flowables(section.get("body", []), styles,
                                       content_width, base_dir))
        if i < len(sections) - 1:
            story.append(PageBreak())

    doc.multiBuild(story)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
