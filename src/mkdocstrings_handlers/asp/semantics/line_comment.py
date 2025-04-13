""" This module contains the LineComment class, which represents a single line comment in an ASP document."""

from __future__ import annotations

from dataclasses import dataclass

from tree_sitter import Node


@dataclass
class LineComment:
    """A line comment in an ASP document."""

    row: int
    """ The row of the line comment. """
    line: str
    """ The line of text of the comment. """

    @staticmethod
    def from_node(node: Node) -> LineComment:
        """
        Create a line comment from a node.
        """
        clean_text = node.text.decode("utf-8").removeprefix("%").strip()

        return LineComment(row=node.start_point.row, line=clean_text)
