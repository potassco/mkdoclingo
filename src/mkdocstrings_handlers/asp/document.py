"""This module contains the Document class, which represents a single document in the context of ASP."""

from __future__ import annotations

from dataclasses import dataclass, field

from tree_sitter import Tree

from mkdocstrings_handlers.asp.semantics.block_comment import BlockComment
from mkdocstrings_handlers.asp.semantics.collector import Collector
from mkdocstrings_handlers.asp.semantics.line_comment import LineComment
from mkdocstrings_handlers.asp.semantics.predicate import Predicate
from mkdocstrings_handlers.asp.semantics.statement import Statement
from mkdocstrings_handlers.asp.tree_sitter.parser import ASPParser


@dataclass
class Document:
    """
    A document representing the content of a particular ASP file.
    """

    title: str
    content: str
    tree: Tree
    statements: list[Statement] = field(default_factory=list)
    line_comments: list[LineComment] = field(default_factory=list)
    block_comments: list[BlockComment] = field(default_factory=list)
    ordered_objects: list[Statement | LineComment | BlockComment] = field(default_factory=list)
    predicates: dict[str, Predicate] = field(default_factory=dict)

    @staticmethod
    def new(title: str, content: str) -> Document:
        """
        Create a new document.

        Args:
            title: The title of the document.
            content: The content of the document.

        Returns:
            The created document.
        """

        # Parse content to tree
        parser = ASPParser()
        tree = parser.parse(content)
        # Collect data from tree
        collector = Collector()
        collector.collect(tree)

        return Document(
            title=title,
            content=content,
            tree=tree,
            statements=collector.statements,
            line_comments=collector.line_comments,
            block_comments=collector.block_comments,
            ordered_objects=collector.ordered_objects,
            predicates=collector.predicates,
        )
