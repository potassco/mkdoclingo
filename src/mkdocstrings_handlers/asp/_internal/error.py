"""This module defines custom exceptions for error handling."""


class ExtractionError(Exception):
    """Raised when the AST is malformed or missing expected text."""
