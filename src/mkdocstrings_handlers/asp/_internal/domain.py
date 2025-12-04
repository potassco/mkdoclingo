from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Include:
    """An include directive in an ASP document."""

    path: Path
    """ The path of the included file."""


@dataclass
class Predicate:
    """A predicate in an ASP program."""

    identifier: str
    arity: int
    negation: bool = False


@dataclass
class LineComment:
    """A line comment in an ASP program."""

    row: int
    """ The row in the source file where the comment is located."""
    content: str
    """ The content of the line comment."""


@dataclass
class Statement:
    """A statement in an ASP program."""

    row: int
    """The row in the source file where the statement is located."""
    text: str
    """The text of the statement."""
    provided_predicates: list[Predicate]
    """The predicates provided by the statement."""
    needed_predicates: list[Predicate]
    """The predicates needed by the statement."""


@dataclass
class Document:
    path: Path
    content: str
    includes: list[Include] = field(default_factory=list)
    statements: list[Statement] = field(default_factory=list)
    ordered_elements: list[Statement | LineComment] = field(default_factory=list)
