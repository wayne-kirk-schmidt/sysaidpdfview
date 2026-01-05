# Architecture — sysaidpdfview

This document describes the architectural decisions, 
execution model, and design trade-offs behind sysaidpdfview.

The goal of this tool is not generic PDF parsing. 
This is deterministic extraction of data from layout-driven PDFs.

---

## Core Philosophy

PDFs are spatial documents first and text documents second.

Most PDF tools treat text as the primary goal and layout as a hint. 

This project intentionally reverses that assumption:

- X/Y geometry is authoritative
- Text is interpreted only within spatial constraints
- Extraction favors determinism over recall

This makes the system predictable, auditable, 
and suitable for operational automation.

---

## High-Level Pipeline

1. inspect	-- initial analysis
   captures: geometry and raw words

2. examine	-- layout-driven state machine 
   captures: records (pairs of keys and values )

3. display	-- render views  (txt, JSON)
   display: for use in programs or for human viewing

The pipeline is cumulative:

- inspect always runs first
- examine depends on inspect
- display depends on both inspect and examine

Invoking "later" verb automatically executes all prerequisite stages.
But only the selected verb controls terminal output.

---

## Execution Model

Execution is driven by a simple pipeline loop:

- The pipeline stages are declared once
- The requested verb determines how far the loop runs
- No stage can execute without its dependencies

This avoids duplicated logic and guarantees behavior across commands.

---

## Phase Responsibilities

### Inspect Phase (inspection/inspector.py)

Responsibility: capture raw, low-level PDF structure.

Produces:
- page metadata
- word geometry
- positional information

Characteristics:
- no interpretation
- no aggregation
- no mutation

This phase answers the question:

What is physically present on the page?

---

### Examine Phase (inspection/examine.py)

Responsibility: convert geometry into structured records.

This is the authoritative extraction engine.

Key behaviors:
- groups words into visual lines by vertical proximity
- classifies words into keys vs values by X-axis zones
- supports multi-line value continuation
- normalizes document identity (TicketType, TicketNumber)

Implementation notes:
- implemented as a single-pass state machine
- intentionally monolithic
- complexity is essential, not accidental

This phase answers the question:

Given the layout, what data is present?

---

### Display Phase (inspection/display.py)

Responsibility: render views over extracted data.

Key constraints:
- no inference
- no mutation
- no re-extraction

Supports:
- document summary views
- key listings
- full record listings
- exact or regex-based selectors

This phase answers the question:

How should the extracted data be presented?

---

## Data Model

### Record

The fundamental unit of extracted data:

page: 1
key: Status
value: Open

Properties:
- immutable
- page-aware
- order-preserving

---

### Document Envelope

Document-level metadata is treated as data, not presentation logic.

document:
- ticket:
  - type: Incident
  - number: 456789
- pages: 3
- record_count: 42
- unique_key_count: 11

Ticket identity is extracted once and propagated structurally.

---

## Script-First Design

This project is intentionally not packaged.

Reasons:
- explicit execution context
- transparent imports
- easier debugging
- no hidden installation semantics

Local modules are used for structure, not for reuse guarantees.

If the tool later evolves into a reusable library, packaging can be added deliberately.

---

## Out of Scope - Ground Rules

This tool explicitly does not attempt to:

- perform OCR
- guess semantic meaning beyond layout
- recover malformed PDFs

These trade-offs are intentional.

---

## Out of Scope - Future Evolution

Possible future extensions:

- regression fixture PDFs
- schema-typed outputs
- diffing between PDF versions
- promotion to a packaged CLI

None of these are required for current correctness.

---

## Summary

sysaidpdfview is designed as a pipeline for extracting 
structured data from layout-driven PDFs.

Its architecture prioritizes:
- determinism over cleverness
- explainability over heuristics
- correctness over convenience

The result is a tool that can be trusted in operational workflows.
