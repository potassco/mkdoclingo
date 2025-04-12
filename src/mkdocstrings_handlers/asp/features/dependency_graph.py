from __future__ import annotations

from dataclasses import dataclass

from mkdocstrings_handlers.asp.document import Document


@dataclass
class DependencyGraphNode:
    """Dependency graph node."""

    predicate: str
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
    def from_document(document: Document) -> "DependencyGraph":
        """
        Create a dependency graph from an ASP document.

        Args:
            document: The ASP document.

        Returns:
            The dependency graph.
        """
        nodes: dict[str, DependencyGraphNode] = {}

        for statement in document.statements:
            for predicate, _ in statement.provided_predicates:
                predicate_key = str(predicate)
                if predicate_key not in nodes:
                    nodes[predicate_key] = DependencyGraphNode(predicate_key, set(), set())

                # Add positive and negative dependencies from needed_predicates
                positive = {str(p) for p, n in statement.needed_predicates if not n}
                negative = {str(p) for p, n in statement.needed_predicates if n}
                nodes[predicate_key].positive.update(positive)
                nodes[predicate_key].negative.update(negative)

        return DependencyGraph(list(nodes.values()))
