""" This module contains the Statement class, which represents a statement in an ASP program."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from tree_sitter import Node

from mkdocstrings_handlers.asp.semantics.predicate import Predicate


@dataclass
class Statement:
    """A statement in an ASP program."""

    row: int
    """The row in the source file where the statement is located."""
    text: str
    """The text of the statement."""
    provided_predicates: list[Tuple[Predicate, bool]]
    """The predicates provided by the statement."""
    needed_predicates: list[Tuple[Predicate, bool]]
    """The predicates needed by the statement."""

    @staticmethod
    def from_node(node: Node) -> Statement:
        """
        Create a statement from a node.
        Args:
            node: The node representing the statement.
        Returns:
            The created statement.
        """
        return Statement(
            row=node.start_point.row, text=node.text.decode("utf-8"), provided_predicates=[], needed_predicates=[]
        )

    def add_provided(self, predicate: Predicate, negation: bool = False):
        """Add a predicate this statement provides."""
        self.provided_predicates.append((predicate, negation))

    def add_needed(self, predicate: Predicate, negation: bool = False):
        """Add a predicate this statement needs."""
        self.needed_predicates.append((predicate, negation))
