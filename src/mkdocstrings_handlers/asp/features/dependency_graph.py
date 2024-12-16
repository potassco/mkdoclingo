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
    def from_document(document: Document) -> DependencyGraph:
        """
        Create a dependency graph from an ASP document.

        Args:
            document: The ASP document.

        Returns:
            The dependency graph.
        """

        nodes: dict[str, DependencyGraphNode] = {}

        for statement in document.statements:
            for provided in statement.provided_literals:
                predicate = f"{provided.identifier}/{provided.arity}"
                positive = set(
                    map(
                        lambda x: f"{x.identifier}/{x.arity}",
                        filter(lambda x: not x.negation, statement.needed_literals),
                    )
                )
                negative = set(
                    map(lambda x: f"{x.identifier}/{x.arity}", filter(lambda x: x.negation, statement.needed_literals))
                )
                if predicate not in nodes:
                    nodes[predicate] = DependencyGraphNode(predicate, set(), set())

                nodes[predicate].positive.update(positive)
                nodes[predicate].negative.update(negative)

        return DependencyGraph(list(nodes.values()))
