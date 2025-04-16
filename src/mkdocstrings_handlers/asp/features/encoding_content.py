"""This module contains the classes for building a dependency graph from an ASP document."""

from __future__ import annotations

from dataclasses import dataclass

from clingo import Control

from mkdocstrings_handlers.asp.document import Document
from mkdocstrings_handlers.asp.semantics.block_comment import BlockComment
from mkdocstrings_handlers.asp.semantics.line_comment import LineComment
from mkdocstrings_handlers.asp.semantics.statement import Statement


def is_clingo_code(code: str) -> bool:
    """
    Check if the given code is clingo code.

    Args:
        code: The code to check.

    Returns:
        True if the code is clingo code, False otherwise.
    """

    def silent_logger(message, _):
        pass  # Ignore all messages

    ctl = Control(["--warn=none"], logger=silent_logger)
    try:
        ctl.add("base", [], code)
        ctl.ground([("base", [])])

        return True
    except Exception:
        return False


@dataclass
class EncodingLine:
    """Line in the encoding."""

    type: str
    """Wither code or md"""
    str_content: str
    """Content of the line"""


@dataclass
class EncodingContent:
    """Content of the encoding including statements and lines."""

    lines: list[EncodingLine]
    """lines of the encoding"""

    @staticmethod
    def from_document(document: Document) -> "EncodingContent":
        """
        Create a encoding content from an ASP document.

        Args:
            document: The ASP document.

        Returns:
            The encoding content.
        """
        lines: list[EncodingLine] = []

        for oo in document.ordered_objects:
            if isinstance(oo, Statement):
                if lines and lines[-1].type == "code":
                    lines[-1].str_content += "\n" + oo.text
                else:
                    lines.append(EncodingLine("code", oo.text))
            if isinstance(oo, BlockComment):
                content = "\n".join(oo.lines)
                lines.append(EncodingLine("md", content))
            if isinstance(oo, LineComment):
                is_code = is_clingo_code(oo.line)
                if not is_code:
                    lines.append(EncodingLine("md", oo.line))
                else:
                    print("Commented code ignored:", oo.line)

        return EncodingContent(lines)
