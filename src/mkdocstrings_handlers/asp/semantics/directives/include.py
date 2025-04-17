""" This module contains the representation of an include directive in ASP."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tree_sitter import Node


@dataclass
class Include:
    """An include directive in an ASP document."""

    path: Path
    """ The path of the included file."""

    @staticmethod
    def from_node(path: Path, node: Node) -> Include:
        """
        Create an Include from the given node.

        Args:
            node: The node.

        Returns:
            The created Include.
        """
        # If the node is an include,
        # then the first child is the include directive
        # and the second child is the file path.

        # The second child of the file path is the file path
        # as a string fragment without the quotes.
        file_path_node = node.children[1]
        file_path = Path(file_path_node.children[1].text.decode("utf-8"))

        # return Include(file_path)
        return Include(path.parent.joinpath(file_path))
