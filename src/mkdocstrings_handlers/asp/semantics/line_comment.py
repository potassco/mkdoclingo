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
        split_lines = node.text.decode("utf-8").split("\n")

        clean_lines = []

        for line in split_lines:
            clean_lines.append(line.removeprefix("%"))

        clean_text = "\n".join(clean_lines)

        return LineComment(row=node.start_point.row, line=clean_text)
