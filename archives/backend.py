"""
Coordination file for pdf processing between all three verb files
"""
from pathlib import Path
import pdfplumber

def load_pdf(path: Path):
    """
    Load the PDF file and do general processing. persist information.
    This structure will be enriched as processing continues.
    """
    pages = []

    with pdfplumber.open(str(path)) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(
                use_text_flow=True,
                keep_blank_chars=False
            )

            lines = []

            for w in words:
                lines.append({
                    "text": w.get("text", ""),
                    "x0": float(w.get("x0", 0.0)),
                    "x1": float(w.get("x1", 0.0)),
                    "top": float(w.get("top", 0.0)),
                    "bottom": float(w.get("bottom", 0.0)),
                })

            if lines:
                x_min = min(l["x0"] for l in lines)
                x_max = max(l["x1"] for l in lines)
                y_min = min(l["top"] for l in lines)
                y_max = max(l["bottom"] for l in lines)
            else:
                x_min = x_max = y_min = y_max = 0.0

            pages.append({
                "page_number": idx,
                "text_items": len(lines),
                "x_min": x_min,
                "x_max": x_max,
                "y_min": y_min,
                "y_max": y_max,
                "lines": lines,
            })

    return {
        "page_count": len(pages),
        "pages": pages,
    }
