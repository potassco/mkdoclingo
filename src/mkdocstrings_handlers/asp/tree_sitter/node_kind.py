""" This module contains the NodeKind class, which represents the kind of a node in the abstract syntax tree."""

from __future__ import annotations

from enum import Enum, auto


class NodeKind(Enum):
    """The kind of a node in the abstract syntax tree."""

    UNKNOWN = auto()
    STATEMENT = "statement"
    HEAD = "head"
    BODY = "body"
    SYMBOLIC_ATOM = "symbolic_atom"
    LITERAL_TUPLE = "literal_tuple"
    LINE_COMMENT = "line_comment"
    BLOCK_COMMENT = "block_comment"
    SHOW_SIGNATURE = "show_signature"
    SHOW = "show"
    SHOW_TERM = "show_term"
    INCLUDE = "include"
    ERROR = "ERROR"

    @staticmethod
    def from_grammar_name(grammar_name: str):
        """
        Create the node kind from the given grammar name.

        This returns NodeKIind.UNKNOWN if the grammar name is not known.

        Args:
            grammar_name: The grammar name.

        Returns:
            The node kind.
        """
        return _node_kind_map.get(grammar_name, NodeKind.UNKNOWN)


_node_kind_map = {kind.value: kind for kind in NodeKind}
"""Map of node kind values to node kinds."""
