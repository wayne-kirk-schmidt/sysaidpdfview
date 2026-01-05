"""
This defines data models being used by sysaidpdfview
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class DocumentRef:
    """
    Class to record the unique identifier of a pdf file, namely a sha256 hash of the contents
    """
    path: str
    sha256: str
    size_bytes: int

@dataclass(frozen=True)
class PageGeometry:
    """
    Class to record the page geometry within the PDF file
    """
    page_number: int
    text_item_count: int
    x_min: float
    x_max: float
    y_min: float
    y_max: float

@dataclass(frozen=True)
class TextLine:
    """
    Class to record if there is a text line in the data
    """
    page_number: int
    text: str
    x0: float
    x1: float
    top: float
    bottom: float

@dataclass(frozen=True)
class RepeatedLine:
    """
    Class to record if there is a repeated line
    """
    text: str
    pages: Tuple[int, ...]

# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class InspectResult:
    """
    Class to capture the results of inspecting a PDF file with pdfplumber
    """
    document: DocumentRef
    page_count: int
    text_based: bool
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    pages: Tuple[PageGeometry, ...]
    lines: Tuple[TextLine, ...]
    repeated_lines: Tuple[RepeatedLine, ...]

@dataclass
class FieldSpan:
    """
    class to compute the dimensions of the keys and values in the PDF
    """
    page: int
    role: str              # "KEY_CANDIDATE"
    text: str
    bbox: tuple            # (x0, y0, x1, y1)
    anchor_x1: float       # left boundary of key zone
    anchor_x2: float       # left boundary of value zone
    source_lines: list[int]
