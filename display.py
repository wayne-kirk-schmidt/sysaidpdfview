"""
Display layer for pdfinspect.

Responsible for rendering views over examined structure.
No mutation. No inference. No side effects beyond printing.
"""

import re
from typing import Any, Dict, List, Optional

Record = Dict[str, Any]  # expects: {"page": int, "key": str, "value": str}


# ============================================================
# Selector helpers
# ============================================================

def _is_regex_selector(selector: Optional[str]) -> bool:
    """
    Determine whether the selector is a regex literal (/.../).
    """
    return (
        bool(selector)
        and selector.startswith("/")
        and selector.endswith("/")
        and len(selector) >= 2
    )

def _compile_selector_regex(selector: str) -> re.Pattern:
    """
    Compile a selector regex of the form /pattern/.
    """
    pattern = selector[1:-1]
    return re.compile(pattern, re.IGNORECASE)


def _unique_in_order(items: List[str]) -> List[str]:
    """
    Preserve unique items in original order.
    """
    seen = set()
    out: List[str] = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


# ============================================================
# Document metadata
# ============================================================

def _extract_ticket_metadata(records: List[Record]) -> Dict[str, Optional[str]]:
    """
    Extract document-level ticket metadata.
    Deterministic: first occurrence wins.
    """
    ticket_type: Optional[str] = None
    ticket_number: Optional[str] = None

    for r in records:
        key = str(r.get("key", ""))
        value = str(r.get("value", "")).strip()

        if not ticket_type and key == "TicketType":
            ticket_type = value or None
        elif not ticket_number and key == "TicketNumber":
            ticket_number = value or None

        if ticket_type and ticket_number:
            break

    return {
        "type": ticket_type,
        "number": ticket_number,
    }


# ============================================================
# Public entry point
# ============================================================

def display_view(
    records: List[Record],
    obj: str,
    selector: Optional[str],
    *,
    as_json: bool = False,
) -> Optional[Any]:
    """
    Display views over examined structure.

    If as_json is False:
      - prints human-readable output
      - returns None

    If as_json is True:
      - returns a JSON-serializable structure
      - prints nothing
    """

    if obj == "document":
        payload = _document_payload(records, selector)
        if as_json:
            return payload
        _print_document(payload)
        return None

    if obj == "keys":
        payload = _keys_payload(records, selector)
        if as_json:
            return payload
        _print_keys(payload)
        return None

    if obj == "records":
        payload = _records_payload(records, selector)
        if as_json:
            return payload
        _print_records(payload)
        return None

    raise ValueError(f"Unknown display object: {obj}")


# ============================================================
# Payload builders - JSON-safe
# ============================================================

def _document_payload(records: List[Record], selector: Optional[str]) -> Dict[str, Any]:
    """
    Build document-level payload.
    """
    mode = selector or "summary"
    if mode not in ("summary", "details"):
        raise ValueError(f"Unknown document selector: {mode}")

    pages = [int(r.get("page", 0)) for r in records] if records else []
    max_page = max(pages) if pages else 0

    keys_all = [str(r.get("key", "")).strip() for r in records if str(r.get("key", "")).strip()]
    keys_unique = _unique_in_order(keys_all)

    ticket = _extract_ticket_metadata(records)

    doc: Dict[str, Any] = {
        "mode": mode,
        "ticket": ticket,
        "pages": max_page,
        "record_count": len(records),
        "unique_key_count": len(set(keys_all)),
        "keys": keys_unique,
    }

    if mode == "details":
        counts: Dict[str, int] = {}
        for k in keys_all:
            counts[k] = counts.get(k, 0) + 1
        doc["key_counts"] = [{"key": k, "count": counts.get(k, 0)} for k in keys_unique]

    return {"document": doc}


def _keys_payload(records: List[Record], selector: Optional[str]) -> Dict[str, Any]:
    """
    Build key-oriented payload.
    """
    keys_all = [str(r.get("key", "")).strip() for r in records if str(r.get("key", "")).strip()]
    keys_unique = _unique_in_order(keys_all)

    if not selector:
        return {"keys": keys_unique}

    if _is_regex_selector(selector):
        rx = _compile_selector_regex(selector)
        matched = [k for k in keys_unique if rx.search(k)]
        return {"selector": selector, "keys": matched}

    wanted = selector
    hits: List[Record] = []
    for r in records:
        if str(r.get("key", "")) == wanted:
            hits.append({
                "page": int(r.get("page", 0)),
                "key": wanted,
                "value": str(r.get("value", "")),
            })

    return {"key": wanted, "records": hits}


def _normalize_records(records: List[Record]) -> List[Record]:
    """
    Normalize record objects for output.
    """
    return [
        {
            "page": r.get("page"),
            "key": r.get("key"),
            "value": r.get("value"),
        }
        for r in records
    ]


def _records_payload(records: List[Record], selector: Optional[str]) -> Dict[str, Any]:
    """
    Build record-oriented payload.
    """
    if not selector:
        return {"records": _normalize_records(records)}

    if _is_regex_selector(selector):
        rx = _compile_selector_regex(selector)
        matched = []
        for r in records:
            k = str(r.get("key", ""))
            v = str(r.get("value", ""))
            if rx.search(k) or rx.search(v):
                matched.append({
                    "page": r.get("page"),
                    "key": r.get("key"),
                    "value": r.get("value"),
                })
        return {
            "selector": selector,
            "records": matched,
        }

    matched = [
        {
            "page": r.get("page"),
            "key": r.get("key"),
            "value": r.get("value"),
        }
        for r in records
        if str(r.get("key", "")) == selector
    ]

    return {
        "key": selector,
        "records": matched,
    }


# ============================================================
# Printers - human-readable
# ============================================================

def _print_document(payload: Dict[str, Any]) -> None:
    doc = payload.get("document", {})
    print("=== DOCUMENT ===")
    print(f"Ticket Type   : {doc.get('ticket', {}).get('type')}")
    print(f"Ticket Number : {doc.get('ticket', {}).get('number')}")
    print(f"Pages         : {doc.get('pages')}")
    print(f"Records       : {doc.get('record_count')}")
    print(f"Unique Keys   : {doc.get('unique_key_count')}")
    print()

    for k in doc.get("keys", []):
        print(f"- {k}")


def _print_keys(payload: Dict[str, Any]) -> None:
    print("=== KEYS ===")
    for k in payload.get("keys", []):
        print(k)


def _print_records(payload: Dict[str, Any]) -> None:
    print("=== RECORDS ===")
    for r in payload.get("records", []):
        page = r.get("page")
        key = r.get("key")
        value = r.get("value")
        print()
        print(f"--- page {page} | {key} ---")
        print(value if value is not None else "")
