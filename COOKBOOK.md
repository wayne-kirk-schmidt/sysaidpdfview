# sysaidpdfview — Cookbook

This cookbook provides practical, copy-and-paste examples for common sysaidpdfview tasks.

Important: argparse subcommands require **all global options** come **before** the verb.

That includes: `--src`, `--json`, and `--verbose`.

Correct pattern:

python sysaidpdfview.py --src <file.pdf> [--json] [--verbose] <verb> [object] [selector]

All examples below follow this rule.

---

## Basic Inspection

Inspect a PDF and print a human-readable summary:

python sysaidpdfview.py --src ticket.pdf inspect

Inspect and emit JSON:

python sysaidpdfview.py --src ticket.pdf --json inspect

---

## Examine (Extraction)

Run layout-driven extraction (no output by default):

python sysaidpdfview.py --src ticket.pdf examine

Show extracted keys (diagnostic output):

python sysaidpdfview.py --src ticket.pdf --verbose examine

---

## Display — Document Summary

Show document-level metadata:

python sysaidpdfview.py --src ticket.pdf display document

Show detailed document summary:

python sysaidpdfview.py --src ticket.pdf display document details

Emit document summary as JSON:

python sysaidpdfview.py --src ticket.pdf --json display document

Emit detailed document summary as JSON:

python sysaidpdfview.py --src ticket.pdf --json display document details

---

## Display — Keys

List all unique keys found:

python sysaidpdfview.py --src ticket.pdf display keys

Filter keys by regex:

python sysaidpdfview.py --src ticket.pdf display keys /Date|Owner|Status/

Emit keys as JSON:

python sysaidpdfview.py --src ticket.pdf --json display keys

Emit filtered keys as JSON:

python sysaidpdfview.py --src ticket.pdf --json display keys /Date|Owner|Status/

---

## Display — Records

Show all extracted records:

python sysaidpdfview.py --src ticket.pdf display records

Show records for a specific key:

python sysaidpdfview.py --src ticket.pdf display records Status

Filter records by regex (matches key or value):

python sysaidpdfview.py --src ticket.pdf display records /error|failed/

Emit records as JSON for automation:

python sysaidpdfview.py --src ticket.pdf --json display records

Emit records for a specific key as JSON:

python sysaidpdfview.py --src ticket.pdf --json display records Status

Emit filtered records as JSON:

python sysaidpdfview.py --src ticket.pdf --json display records /error|failed/

---

## Automation-Friendly Usage

Pipe JSON output into jq:

python sysaidpdfview.py --src ticket.pdf --json display records | jq .

Extract a specific field:

python sysaidpdfview.py --src ticket.pdf --json display records Status | jq '.records[].value'

---

## Notes

- Global options (`--src`, `--json`, `--verbose`) must appear before the verb
- Regex selectors must be wrapped in `/.../`
- Matching is case-insensitive
