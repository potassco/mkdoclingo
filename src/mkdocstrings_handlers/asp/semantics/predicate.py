""" This module contains the Predicate class, which holds information about a specific ASP predicate."""

from __future__ import annotations

import string
from dataclasses import dataclass

from tree_sitter import Node

from mkdocstrings_handlers.asp.semantics.predicate_documentation import PredicateDocumentation


@dataclass
class Predicate:
    """A predicate in an ASP document."""

    identifier: str
    """ The identifier of the predicate."""

    arity: int
    """ The arity of the predicate."""

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

        Returns:
            The string representation of the predicate.
        """
        return f"{self.identifier}/{self.arity}"

    @property
    def signature(self) -> str:
        """
        Return the signature of the predicate.

        If the predicate has documentation, return the signature from the documentation.
        Otherwise, return the default signature.

        The default signature is of the form `identifier(A, B, C)` where `A`, `B`, and `C` are
        the first three uppercase letters of the alphabet.

        Returns:
            The signature of the predicate.
        """
        if self.documentation is not None:
            return self.documentation.signature

        return f"{self.identifier}({", ".join(string.ascii_uppercase[:self.arity])})"
