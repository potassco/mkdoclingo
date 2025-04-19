"""This module contains the classes for building a dependency graph from an ASP document."""

from __future__ import annotations

from dataclasses import dataclass

from mkdocstrings_handlers.asp.document import Document
from mkdocstrings_handlers.asp.semantics.predicate import Predicate


@dataclass
class DependencyGraphNode:
    """Dependency graph node."""

    signature: str
    """The predicate this node represents."""
    positive: set[str]
    """The positive dependencies of the predicate."""
    negative: set[str]
    """The negative dependencies of the predicate."""


@dataclass
class DependencyGraph:
    """Dependency graph of an ASP document."""

    nodes: list[DependencyGraphNode]
    """The nodes of the dependency graph."""

    @staticmethod
    def from_document(documents: list[Document]) -> "DependencyGraph":
        """
        Create a dependency graph from a list of ASP documents.

        Args:
            documents: The list of documents to create the graph from.

        Returns:
            The dependency graph.
        """
        nodes: dict[str, DependencyGraphNode] = {}

        # Find all provided predicates and their dependencies
        for document in documents:
            for statement in document.statements:
                for predicate, _ in statement.provided_predicates:
                    signature = predicate.signature
                    if signature not in nodes:
                        nodes[signature] = DependencyGraphNode(signature, set(), set())

                    # Add positive and negative dependencies from needed_predicates
                    positive = {p.signature for p, n in statement.needed_predicates if not n}
                    negative = {p.signature for p, n in statement.needed_predicates if n}
                    nodes[signature].positive.update(positive)
                    nodes[signature].negative.update(negative)

        # Find all predicates that are not provided but are used in the document
        # these predicates are considered inputs
        for document in documents:
            for signature, predicate in document.predicates.items():
                if signature not in nodes:
                    nodes[signature] = DependencyGraphNode(signature, set(), set())
                    predicate.is_input = True

        return DependencyGraph(list(nodes.values()))
