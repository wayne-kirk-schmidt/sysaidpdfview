# sysaidpdfview

SysAid PDF layout driven inspection and examination tool.

`sysaidpdfview` is a **deterministic geometry-first PDF parser**. 
That means where possible, it avoids regular expressions.

This means this should work on any Service Record printed from SysAid in Classic View.

And while this is starting with SysAID, this can be extended to other similar style reports (JIRA).

It starts with the idea that there is a form in the report and looks to find out the boundaries of key and value.

As a result, we get toavoid avoiding brittle regex scraping and fuzzy OCR heuristics.

The project is intentionally built as **a script plus local modules**
This is not a packaged library yet to provide a simple solution. 

---

---

## Important Documentation

- [Overview](README.md)  
  This document. General overview of the tool and abilities.

- [Architecture](ARCHITECTURE.md)  
  Design decisions, execution model, and pipeline rationale.

- [Cookbook](COOKBOOK.md)  
  Practical, copy-and-paste command-line examples.

## Design Principles

- **Geometry first** – extraction is driven by X/Y coordinates, not guessy text patterns
- **Deterministic** – same input PDF always produces the same output
- **Explainable** – every extracted value can be traced back to page and coordinates
- **No mutation** – source PDFs are never altered
- **Pipeline separation** – inspect → examine → display
- **Tooling-clean** – pylint clean with intentional, documented exceptions only

---

## Pipeline Overview

```
PDF
 │
 ▼
inspect   → raw geometry, words, lines
 │
 ▼
examine   → layout-driven key/value records (authoritative)
 │
 ▼
display  → human or JSON views over extracted structure
```

**Execution model:**  
The pipeline is cumulative. Invoking a later verb automatically executes all 
prior stages, but only the selected verb controls final output.

---

## Repository Layout

```
sysaidpdfview/
├── sysaidpdfview.py          # CLI script (entry point)
├── inspection/
│   ├── __init__.py
│   ├── inspector.py      # inspect phase (geometry extraction)
│   ├── examine.py        # examine phase (layout → records)
│   └── display.py        # display phase (views / JSON)
└── models.py              # shared data structures
```

---

## Installation

This project intentionally does **not** require packaging or installation.

### Requirements

- Python 3.9+
- `pdfplumber`

```bash
pip install pdfplumber
```

Clone the repository and run directly.

---

## Usage

```bash
python sysaidpdfview.py --src <file.pdf> <verb> [options]
```

### Global Options

| Option | Description |
|------|-------------|
| `--src` | Path to PDF file (required) |
| `--json` | Emit JSON instead of human output |
| `--verbose` | Enable verbose diagnostics (future-proofed) |

---

## Verbs

### inspect

Inspect raw PDF geometry and structure.

```bash
python sysaidpdfview.py --src ticket.pdf inspect
```

```bash
python sysaidpdfview.py --src ticket.pdf inspect --json
```

---

### examine

Perform **layout-driven key/value extraction**.

```bash
python sysaidpdfview.py --src ticket.pdf examine
```

This phase is the **authoritative extraction engine**. It:

- groups words into visual lines
- separates keys vs values by X-axis zones
- supports multi-line value continuation
- normalizes ticket identity into:
  - `TicketType`
  - `TicketNumber`

---

### display

Render views over examined structure.

```bash
python sysaidpdfview.py --src ticket.pdf display document
python sysaidpdfview.py --src ticket.pdf display keys
python sysaidpdfview.py --src ticket.pdf display records
```

Add `--json` to receive structured output suitable for automation.

---

## Output Model

### Record

```json
{
  "page": 1,
  "key": "Status",
  "value": "Open"
}
```

### Document Envelope

```json
{
  "document": {
    "ticket": {
      "type": "Incident",
      "number": "456789"
    },
    "pages": 3,
    "record_count": 42,
    "unique_key_count": 11,
    "keys": ["Status", "Owner", "Priority"]
  }
}
```

---

## Linting

Because this is a script with local modules, run pylint as:

```bash
pylint --init-hook='import sys; sys.path.insert(0, ".")' sysaidpdfview.py
```

---

## License

Apache 2.0

---

## Author

Wayne Kirk Schmidt  
ChangeIS K.K.
