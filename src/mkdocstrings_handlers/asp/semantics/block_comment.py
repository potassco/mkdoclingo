""" This module contains the representation of a block or multi-line comment in an ASP document."""

from __future__ import annotations

from dataclasses import dataclass

from tree_sitter import Node


@dataclass
class BlockComment:
    """A block comment in an ASP document."""

    row: int
    """ The row of the block comment. """
    lines: list[str]
    """ The lines of text of the block comment. """

    @staticmethod
    def from_node(node: Node) -> BlockComment:
        """
        Create a block comment from a node.
        """
        clean_text = node.text.decode("utf-8").removeprefix("%*").removesuffix("*%").strip()
        lines = clean_text.split("\n")

        return BlockComment(row=node.start_point.row, lines=lines)
