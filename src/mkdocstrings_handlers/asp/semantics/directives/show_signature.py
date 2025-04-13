""" This module contains the representation of a show signature directive in ASP."""

from __future__ import annotations

from dataclasses import dataclass

from tree_sitter import Node


@dataclass
class ShowSignature:
    """A show signature directive in an ASP document."""

    signature: str
    """ The signature of the show directive."""

    @staticmethod
    def from_node(node: Node) -> ShowSignature:
        """
        Create a ShowSignature from the given node.

        Args:
            node: The node.

        Returns:
            The created ShowSignature.
        """
        # If the node is a show_signature,
        # then the first child is the show directive
        # and the second child is the signature.

        signature = node.children[1].text.decode("utf-8")

        return ShowSignature(signature)
