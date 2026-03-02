"""
cbml-parser — A parser for CBML (Comic Book Markup Language).

Basic usage:

    from cbml_parser import CBMLParser

    parser = CBMLParser()
    comic  = parser.parse_file("my_comic.cbml")
    result = parser.validate_file("my_comic.cbml")
"""

from cbml_parser.parser import CBMLParser
from cbml_parser.models import Comic, Page, Panel, Slot, Caption, DialogueLine, PresetLayout, CustomGrid
from cbml_parser.validator import ValidationResult
from cbml_parser.exceptions import CBMLError, CBMLParseError, CBMLValidationError

__version__ = "1.0.0"

__all__ = [
    "CBMLParser",
    "Comic",
    "Page",
    "Panel",
    "Slot",
    "Caption",
    "DialogueLine",
    "PresetLayout",
    "CustomGrid",
    "ValidationResult",
    "CBMLError",
    "CBMLParseError",
    "CBMLValidationError",
]