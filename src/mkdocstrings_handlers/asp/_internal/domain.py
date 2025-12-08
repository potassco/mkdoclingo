from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path


@dataclass
class Include:
    """An include directive in an ASP document."""

    path: Path
    """ The path of the included file."""


class ShowStatus(IntEnum):
    """Enum for predicate show status with bitwise-compatible values."""

    DEFAULT = 0
    EXPLICIT = 1
    PARTIAL = 2
    PARTIAL_AND_EXPLICIT = 3
    HIDDEN = 4


@dataclass
class Show:
    """A show directive in an ASP document."""

    predicate: Predicate
    """ The predicate supposed to be shown."""

    status: ShowStatus = ShowStatus.DEFAULT
    """ The show status of the predicate."""

@dataclass
class Predicate:
    """A predicate in an ASP program."""

    identifier: str
    arity: int
    negation: bool = False

    @property
    def signature(self) -> str:
        """
        Return the signature of the predicate.

        The signature of a predicate is a string of the form `identifier/arity`.

        Returns:
            The signature of the predicate.
        """
        return f"{self.identifier}/{self.arity}"


@dataclass
class LineComment:
    """A line comment in an ASP program."""

    row: int
    """ The row in the source file where the comment is located."""
    content: str
    """ The content of the line comment."""


@dataclass
class BlockComment:
    """A block comment in an ASP program."""

    row: int
    """ The row in the source file where the comment starts."""
    content: str
    """ The content of the block comment."""


@dataclass
class Statement:
    """A statement in an ASP program."""

    row: int
    """The row in the source file where the statement is located."""
    content: str
    """The content of the statement."""
    provided_predicates: list[Predicate]
    """The predicates provided by the statement."""
    needed_predicates: list[Predicate]
    """The predicates needed by the statement."""

@dataclass
class ArgumentDocumentation:
    identifier: str
    description: str

@dataclass
class PredicateDocumentation:
    row: int
    content: str
    signature: str
    description:str
    arguments: list[ArgumentDocumentation]

@dataclass
class Document:
    path: Path
    content: str
    includes: list[Include] = field(default_factory=list)
    statements: list[Statement] = field(default_factory=list)
    line_comments: list[LineComment] = field(default_factory=list)
    block_comments: list[BlockComment] = field(default_factory=list)
    predicate_documentations: list[PredicateDocumentation] = field(default_factory=list)
