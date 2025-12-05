"""This module contains the NodeKind class, which represents the kind of a node in the abstract syntax tree."""

from __future__ import annotations

from enum import Enum, auto
from pathlib import Path

import tree_sitter_clingo
from tree_sitter import Language, Node, Parser, Query, QueryCursor

_LANGUAGE = Language(tree_sitter_clingo.language())
_QUERY_DIR = Path(__file__).parent / "queries"


def get_parser() -> Parser:
    """Factory to get a configured parser instance."""
    return Parser(_LANGUAGE)


class NodeKind(Enum):
    """The kind of a node in the abstract syntax tree."""

    UNKNOWN = auto()
    RULE = "rule"
    INTEGRITY_CONSTRAINT = "integrity_constraint"
    INCLUDE = "include"
    ATOM = "symbolic_atom"
    ERROR = "ERROR"
    LINE_COMMENT = "line_comment"
    BLOCK_COMMENT = "block_comment"

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


class AspQuery:
    """
    Wraps a Tree-sitter S-Expression.
    Handles file loading and cursor management automatically.
    """

    def __init__(self, filename: str):
        self.filename = filename
        self._query: Query | None = None

    @property
    def query(self) -> Query:
        """Lazy load the query on first access."""
        if self._query is None:
            try:
                with open(_QUERY_DIR / self.filename, "rb") as f:
                    self._query = Query(_LANGUAGE, f.read())
            except FileNotFoundError:
                raise RuntimeError(
                    f"Missing SCM file: {self.filename}. "
                )
        return self._query

    def captures(self, node: Node) -> dict[str, list[Node]]:
        """
        Run the query on a node and return a clean dictionary of captures.
        """
        cursor = QueryCursor(self.query)
        return cursor.captures(node)


class Queries:
    """Registry of available Semantic Queries."""

    BODY = AspQuery("body.scm")
    HEAD = AspQuery("head.scm")
    PREDICATE = AspQuery("predicate.scm")
    DOC_PREDICATE = AspQuery("documentation_predicate.scm")
    DOC_ARGUMENT = AspQuery("documentation_argument.scm")
