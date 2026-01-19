#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exaplanation: sysaidpdfview. Review sysaid PDF files based on geometry.

Usage:
   $ python  sysaidpdfview  <subject> <verb> <object> [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           sysaidpdfview
    @version        1.00
    @author-name    Wayne Kirk Schmidt
    @author-email   wayne.kirk.schmidt@changeis.co.jp
    @author-email   wayne.kirk.schmidt@gmail.com
    @license-name   Apache
    @license-url    https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = 1.00
__author__ = "Wayne Kirk Schmidt (wayne.kirk.schmidt@changeis.co.jp)"

from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode = True

# ==================================================================
# Script Execution Order of Processing
# ==================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# pylint: disable=wrong-import-position
from inspection.inspector import inspect_pdf, inspect_to_text, inspect_to_json
from inspection.examine import extract_records, print_keys
from inspection.display import display_view

# ==================================================================
# Pipeline Processing Stages 
# ==================================================================

PIPELINE = ("inspect", "examine", "display")


def complain_and_exit(msg: str) -> None:
    """
    Raise a generic error. To be improved with logging module
    """
    raise SystemExit(msg)


# ==================================================================
# CLI
# ==================================================================

def build_parser() -> argparse.ArgumentParser:
    """
    Assemble both options as well as arguments 
    """
    parser = argparse.ArgumentParser(
        prog="sysaidpdfview",
        description="Layout-driven PDF inspection and examination tool"
    )

    # ===================
    # Global options
    # ===================
    parser.add_argument(
        "--src",
        type=Path,
        required=True,
        help="PDF file to inspect"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output where applicable"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose diagnostics"
    )

    subparsers = parser.add_subparsers(dest="verb", required=True)

    # ===================
    # Inspect
    # ===================
    subparsers.add_parser(
        "inspect",
        help="Measure physical PDF properties"
    )

    # ===================
    # Examine
    # ===================
    subparsers.add_parser(
        "examine",
        help="Infer document structure"
    )

    # ===================
    # Display
    # ===================
    display_p = subparsers.add_parser(
        "display",
        help="Display views over examined structure"
    )
    display_p.add_argument(
        "object",
        choices=["document", "keys", "records"]
    )
    display_p.add_argument(
        "selector",
        nargs="?",
        default=None
    )

    return parser


# ==================================================================
# Entry point
# ==================================================================


def main(argv=None):
    """
    Main entry point for the code. This is a script.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verb not in PIPELINE:
        complain_and_exit(f"Unknown verb: {args.verb}")

    pdf_path = args.src
    target_idx = PIPELINE.index(args.verb)
    results = {}

    for idx, stage in enumerate(PIPELINE):
        if idx > target_idx:
            break

        if stage == "inspect":
            results["inspect"] = inspect_pdf(
                pdf_path,
                verbose=args.verbose
            )

        if stage == "examine":
            records = extract_records(results["inspect"])
            results["examine"] = records

        if stage == "display":
            payload = display_view(
                results["examine"],
                args.object,
                args.selector,
                as_json=args.json,
            )

            if args.json and payload is not None:
                print(json.dumps(payload, indent=2))

    # ==================================================================
    # Process Render terminal stage only
    # ==================================================================

    if args.verb == "inspect":
        result = results["inspect"]
        if args.json:
            print(inspect_to_json(result))
        else:
            print(inspect_to_text(result))
        return

    if args.verb == "examine":
        if args.verbose:
            print_keys(results["inspect"])
        return


if __name__ == "__main__":
    main()
