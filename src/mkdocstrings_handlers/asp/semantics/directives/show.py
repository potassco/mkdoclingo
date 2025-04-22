""" This module contains the representation of a show directive in ASP."""

from __future__ import annotations

from dataclasses import dataclass

from tree_sitter import Node

from mkdocstrings_handlers.asp.semantics.predicate import Predicate, ShowStatus
from mkdocstrings_handlers.asp.tree_sitter.node_kind import NodeKind


@dataclass
class Show:
    """A show directive in an ASP document."""

    predicate: Predicate
    """ The predicate supposed to be shown."""

    disable_default: bool = False
    """ If this show directive disables the default show behaviour."""

    @staticmethod
    def from_node(node: Node) -> Show | None:
        """
        Create a Show directive from the given node.

        Args:
            node: The node.

        Returns:
            The created Show directive representation if it was valid and non-empty,
            None otherwise.
        """
        match NodeKind.from_grammar_name(node.grammar_name):
            # The show_signature node has two children:
            # 1. The show directive
            # 2. The signature in form identifier/arity
            case NodeKind.SHOW_SIGNATURE:
                identifier, arity = node.children[1].text.decode("utf-8").split("/")
                return Show(Predicate(identifier, int(arity), show_status=ShowStatus.EXPLICIT), disable_default=True)

            # The show_term node has two children:
            # 1. The show directive
            # 2. The term with the function as a first child
            case NodeKind.SHOW_TERM:
                function = node.children[1].children[0]

                if function.child_count == 1:
                    # if the function has only one child, then it has no arguments
                    # this means the text is the identifier and the arity is 0
                    identifier = function.children[0].text.decode("utf-8")
                    arity = 0
                else:
                    # If the function has more than one child, then it has arguments
                    # the first child is the identifier and the second is
                    # the argument pool with terms as children
                    identifier = function.children[0].text.decode("utf-8")
                    arity = len(function.children[1].children[0].children) // 2

                return Show(Predicate(identifier, int(arity), show_status=ShowStatus.PARTIAL))

        return None
