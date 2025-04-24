"""This module contains the Predicate class, which holds information about a specific ASP predicate."""

from __future__ import annotations

import string
from dataclasses import dataclass
from enum import IntEnum

from tree_sitter import Node

from mkdocstrings_handlers.asp.semantics.predicate_documentation import PredicateDocumentation


class ShowStatus(IntEnum):
    """Enum for predicate show status with bitwise-compatible values."""

    DEFAULT = 0
    EXPLICIT = 1
    PARTIAL = 2
    PARTIAL_AND_EXPLICIT = 3
    HIDDEN = 4


@dataclass
class Predicate:
    """A predicate in an ASP document."""

    identifier: str
    """ The identifier of the predicate."""

    arity: int
    """ The arity of the predicate."""

    is_input: bool = False
    """ If it is an input (Not defined by any rule)."""

    show_status: ShowStatus = ShowStatus.DEFAULT
    """ The show status of the predicate."""

    documentation: PredicateDocumentation | None = None
    """ The documentation of the predicate."""

    @staticmethod
    def from_node(node: Node) -> Predicate:
        """
        Create a predicate from a node.

        Args:
            node: The node representing the predicate.

        Returns:
            The created predicate.
        """
        atom = node.children[0] if node.child_count == 1 else node.children[1]

        identifier = atom.children[0].text.decode("utf-8")

        if atom.child_count == 1:
            arity = 0
        else:
            terms = atom.children[1].children[0]
            arity = len(terms.children) // 2

        return Predicate(identifier, arity)

    def __str__(self) -> str:
        """
        Return the string representation of the predicate.

        If the predicate has documentation, return the representation from the documentation.
        Otherwise, return the default representation.

        The default representation is of the form `identifier(A, B, C)` where `A`, `B`, and `C` are
        the first three uppercase letters of the alphabet.

        Returns:
            The string representation of the predicate.
        """
        if self.documentation is not None:
            return self.documentation.signature
        args = ", ".join(string.ascii_uppercase[: self.arity])
        return f"{self.identifier}({args})"

    @property
    def signature(self) -> str:
        """
        Return the signature of the predicate.

        The signature of a predicate is a string of the form `identifier/arity`.

        Returns:
            The signature of the predicate.
        """
        return f"{self.identifier}/{self.arity}"

    def update_show_status(self, status: ShowStatus) -> None:
        """
        Update the show status of the predicate.

        Args:
            status: The new show status.
        """
        if self.show_status == ShowStatus.DEFAULT:
            self.show_status = status
        else:
            self.show_status |= status

        if self.show_status > ShowStatus.HIDDEN:
            self.show_status &= ShowStatus.PARTIAL_AND_EXPLICIT
