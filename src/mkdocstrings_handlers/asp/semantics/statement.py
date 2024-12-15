from __future__ import annotations

from dataclasses import dataclass

from tree_sitter import Node

from .literal import Literal


@dataclass
class Statement:
    """A statement in an ASP program."""

    row: int
    """The row in the source file where the statement is located."""
    text: str
    """The text of the statement."""
    provided_literals: list[Literal]
    """The literals provided by the statement."""
    needed_literals: list[Literal]
    """The literals needed by the statement."""

    @staticmethod
    def from_node(node: Node) -> Statement:
        return Statement(
            row=node.start_point.row, text=node.text.decode("utf-8"), provided_literals=[], needed_literals=[]
        )

    def add_provided(self, literal: Literal):
        self.provided_literals.append(literal)

    def add_needed(self, literal: Literal):
        self.needed_literals.append(literal)
