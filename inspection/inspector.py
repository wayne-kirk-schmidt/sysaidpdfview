"""
collection of functions for the verb inspect for sysaidpdfview
"""
import hashlib
from pathlib import Path
from collections import defaultdict
import json
from dataclasses import asdict

from models import DocumentRef, PageGeometry, TextLine, RepeatedLine, InspectResult
from inspection.backend import load_pdf


def sha256_file(path: Path) -> str:
    """
    Build a SHA256 hash of the file. this is our unique identifier for the file
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# pylint: disable=too-many-locals
def inspect_pdf(path: Path, verbose: bool = False) -> InspectResult:
    """
    Inspect the basic information of the PDF being loaded
    Persist the information learned. 
    """
    pdf = load_pdf(path)
    sha = sha256_file(path)
    size = path.stat().st_size

    document = DocumentRef(str(path), sha, size)

    pages = []
    lines = []
    line_occurrences = defaultdict(list)

    for p in pdf["pages"]:
        page_number = p["page_number"]

        for raw_line in p["lines"]:

            # ---- normalize backend line shape ----
            if isinstance(raw_line, dict):
                text = raw_line.get("text", "")
                x0 = raw_line.get("x0", p["x_min"])
                x1 = raw_line.get("x1", p["x_max"])
                top = raw_line.get("top", p["y_min"])
                bottom = raw_line.get("bottom", p["y_max"])
            else:
                text = str(raw_line)
                x0 = p["x_min"]
                x1 = p["x_max"]
                top = p["y_min"]
                bottom = p["y_max"]

            text = text.strip()
            if not text:
                continue

            line_occurrences[text].append(page_number)

            lines.append(
                TextLine(
                    page_number=page_number,
                    text=text,
                    x0=x0,
                    x1=x1,
                    top=top,
                    bottom=bottom
                )
            )

        pages.append(
            PageGeometry(
                page_number=page_number,
                text_item_count=p["text_items"],
                x_min=p["x_min"],
                x_max=p["x_max"],
                y_min=p["y_min"],
                y_max=p["y_max"]
            )
        )

    repeated = tuple(
        RepeatedLine(text=k, pages=tuple(v))
        for k, v in line_occurrences.items()
        if len(v) > 1
    )

    if pages:
        x_min = min(pg.x_min for pg in pages)
        x_max = max(pg.x_max for pg in pages)
        y_min = min(pg.y_min for pg in pages)
        y_max = max(pg.y_max for pg in pages)
    else:
        x_min = x_max = y_min = y_max = 0.0

    return InspectResult(
        document=document,
        page_count=pdf["page_count"],
        text_based=bool(pages),
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        pages=tuple(pages),
        lines=tuple(lines),
        repeated_lines=repeated
    )


def inspect_to_text(result: InspectResult) -> str:
    """
    Provide a text output of the basic information from the PDF file
    """
    out = []
    out.append("Inspect summary")
    out.append("---------------")
    out.append(f"Path:         {result.document.path}")
    out.append(f"SHA-256:      {result.document.sha256}")
    out.append(f"Size (bytes): {result.document.size_bytes}")
    out.append(f"Pages:        {result.page_count}")
    out.append(f"Text-based:   {result.text_based}")
    out.append(f"X range:      {result.x_min} – {result.x_max}")
    out.append(f"Y range:      {result.y_min} – {result.y_max}")

    if result.repeated_lines:
        out.append("Repeated lines:")
        for rl in result.repeated_lines:
            pages = ",".join(map(str, rl.pages))
            out.append(f"  - {rl.text!r} (pages {pages})")
    else:
        out.append("Repeated lines: none")

    return "\n".join(out)


def inspect_to_json(result: InspectResult) -> str:
    """
    Provide a JSON output of the basic information from the PDF file
    """
    return json.dumps(asdict(result), indent=2)
