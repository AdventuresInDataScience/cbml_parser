from __future__ import annotations


class CBMLError(Exception):
    """Base class for all cbml-parser exceptions."""


class CBMLValidationError(CBMLError):
    """
    Raised when a CBML document contains one or more validation errors
    that prevent parsing from completing successfully.

    Attributes
    ----------
    errors : list[str]
        Blocking errors that make the document invalid.
    warnings : list[str]
        Non-blocking issues that were detected during parsing.
    """

    def __init__(self, errors: list[str], warnings: list[str] | None = None):
        self.errors = errors
        self.warnings = warnings or []
        error_summary = "\n  ".join(errors)
        super().__init__(f"CBML validation failed with {len(errors)} error(s):\n  {error_summary}")


class CBMLParseError(CBMLError):
    """
    Raised when a CBML document cannot be parsed due to a structural issue
    (e.g. a completely malformed line or unexpected state).

    Attributes
    ----------
    line_number : int
        The 1-indexed line number where the error occurred.
    line : str
        The raw content of the offending line.
    message : str
        A description of the parse failure.
    """

    def __init__(self, message: str, line_number: int, line: str):
        self.message = message
        self.line_number = line_number
        self.line = line
        super().__init__(f"Line {line_number}: {message} — got: {line!r}")