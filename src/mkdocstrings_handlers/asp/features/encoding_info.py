"""This module contains the classes for building a dependency graph from an ASP document."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from clingo import Control

from mkdocstrings_handlers.asp.document import Document
from mkdocstrings_handlers.asp.semantics.block_comment import BlockComment
from mkdocstrings_handlers.asp.semantics.line_comment import LineComment
from mkdocstrings_handlers.asp.semantics.statement import Statement

log = logging.getLogger(__name__)


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


class EncodingLineType:
    """Type of the encoding line."""

    CODE = "code"
    """Code line"""
    MD = "md"
    """Markdown line"""


@dataclass
class EncodingLine:
    """Line in the encoding."""

    type: str
    """Wither code or md"""
    str_content: str
    """Content of the line"""


@dataclass
class Encoding:
    source: str
    """Raw source code of the encoding."""
    content: list[EncodingLine]
    statements: list[Statement]

    predicates: list[str]


@dataclass
class EncodingInfo:
    """Content of the encoding including statements and lines."""

    encodings: dict[str, Encoding]

    @staticmethod
    def from_documents(documents: list[Document]) -> EncodingInfo:
        """
        Create a encoding content from an ASP document.

        Args:
            document: The ASP document.

        Returns:
            The encoding content.
        """
        encodings: dict[str, Encoding] = {}

        for document in documents:
            lines: list[EncodingLine] = []

            for oo in document.ordered_objects:
                if isinstance(oo, Statement):
                    if lines and lines[-1].type == EncodingLineType.CODE:
                        lines[-1].str_content += "\n" + oo.text
                    else:
                        lines.append(EncodingLine(EncodingLineType.CODE, oo.text))
                if isinstance(oo, BlockComment):
                    content = "\n".join(oo.lines)
                    lines.append(EncodingLine(EncodingLineType.MD, content))
                if isinstance(oo, LineComment):
                    is_code = is_clingo_code(oo.line)
                    if not is_code:
                        lines.append(EncodingLine(EncodingLineType.MD, oo.line))
                    else:
                        log.debug("Commented code ignored:", oo.line)

            encodings[document.path] = Encoding(
                source=document.content,
                content=lines,
                statements=document.statements,
                predicates=[predicate.signature for predicate in document.predicates.values()],
            )

        return EncodingInfo(encodings)
