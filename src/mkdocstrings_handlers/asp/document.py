"""This module contains the Document class, which represents a single document in the context of ASP."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mkdocstrings_handlers.asp.semantics.block_comment import BlockComment
from mkdocstrings_handlers.asp.semantics.directives.include import Include
from mkdocstrings_handlers.asp.semantics.line_comment import LineComment
from mkdocstrings_handlers.asp.semantics.predicate import Predicate
from mkdocstrings_handlers.asp.semantics.statement import Statement


@dataclass
class Document:
    """
    A document representing the content of a particular ASP file.
    """

    path: Path
    content: str
    statements: list[Statement] = field(default_factory=list)
    line_comments: list[LineComment] = field(default_factory=list)
    block_comments: list[BlockComment] = field(default_factory=list)
    ordered_objects: list[Statement | LineComment | BlockComment] = field(default_factory=list)
    predicates: dict[str, Predicate] = field(default_factory=dict)
    includes: list[Include] = field(default_factory=list)
    disable_default_show: bool = False
