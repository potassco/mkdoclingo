"""This module defines data classes representing ASP documents and their components."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntFlag
from pathlib import Path


@dataclass
class LocatedContent:
    """Source content tracked with its row in the file."""

    row: int
    """ The row in the source file where the fragment is located. """
    content: str
    """ The original content of the fragment. """


@dataclass
class Include(LocatedContent):
    """An include directive in an ASP document."""

    path: Path
    """ The path of the included file."""


class ShowStatus(IntFlag):
    """Enum for predicate show status with bitwise-compatible values."""

    DEFAULT = 0
    """ Default show status when now show directive is present. """
    EXPLICIT = 1
    """ Explicitly shown via a show signature directive."""
    PARTIAL = 2
    """ Partially shown via a show term directive."""
    PARTIAL_AND_EXPLICIT = EXPLICIT | PARTIAL
    """ Both partially and explicitly shown."""
    HIDDEN = 4
    """ Hidden via a show directive without the predicate."""


@dataclass
class Show(LocatedContent):
    """A show directive in an ASP document."""

    predicate: Predicate | None
    """ The predicate supposed to be shown."""

    status: ShowStatus = ShowStatus.DEFAULT
    """ The show status of the predicate."""


@dataclass
class Predicate:
    """A predicate in an ASP program."""

    identifier: str
    """ The identifier of the predicate."""
    arity: int
    """ The arity, the number of arguments, of the predicate."""
    negation: bool = False
    """ Whether the predicate is (default) negated."""

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
class LineComment(LocatedContent):
    """A line comment in an ASP program."""


@dataclass
class BlockComment(LocatedContent):
    """A block comment in an ASP program."""


@dataclass
class Statement(LocatedContent):
    """A statement in an ASP program."""

    provided_predicates: list[Predicate]
    """The predicates provided by the statement."""
    needed_predicates: list[Predicate]
    """The predicates needed by the statement."""


@dataclass
class ArgumentDocumentation:
    """Documentation for a predicate argument."""

    identifier: str
    """ The identifier of the argument. """
    description: str
    """ The description of the argument. """


@dataclass
class PredicateDocumentation(LocatedContent):
    """Documentation for a predicate."""

    signature: str
    """ The signature of the predicate being documented. """
    description: str
    """ The description of the predicate. """
    arguments: list[ArgumentDocumentation]
    """ The list of documented arguments. """


# pylint: disable=too-many-instance-attributes
@dataclass
class Document:
    """An ASP document representing a parsed ASP file."""

    path: Path
    """ The path to the ASP file. """
    content: str
    """ The raw content of the ASP file. """
    includes: list[Include] = field(default_factory=list)
    """ Include directives in the document. """
    statements: list[Statement] = field(default_factory=list)
    """ Statements in the document. """
    line_comments: list[LineComment] = field(default_factory=list)
    """ Line comments in the document. """
    block_comments: list[BlockComment] = field(default_factory=list)
    """ Block comments in the document. """
    predicate_documentations: list[PredicateDocumentation] = field(default_factory=list)
    """ Predicate documentations in the document. """
    shows: list[Show] = field(default_factory=list)
    """ Show directives in the document. """
