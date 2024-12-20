from __future__ import annotations

from dataclasses import dataclass

from mkdocstrings_handlers.asp.document import Document


@dataclass
class Predicate:
    """Dependency graph node."""

    name: str
    """Predicate name."""
    arity: int
    """Arity."""
    # TODO we could add the information of wether it it shown or defined


@dataclass
class PredicateList:
    """List of predicates."""

    predicates: list[Predicate]
    """The predicates in the document."""

    @staticmethod
    def from_document(document: Document) -> PredicateList:
        """
        Creates a list of predicates from an ASP document.

        Args:
            document: The ASP document.

        Returns:
            List of predicates.
        """

        predicates: dict[str, Predicate] = {}

        for statement in document.statements:
            for provided in statement.provided_literals:
                predicate = f"{provided.identifier}/{provided.arity}"
                if predicate not in predicates:
                    predicates[predicate] = Predicate(provided.identifier, provided.arity)

        return PredicateList(list(predicates.values()))
