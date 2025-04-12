""" This module contains the classes for building a glossary from an ASP document."""

from __future__ import annotations

from dataclasses import dataclass

from mkdocstrings_handlers.asp.document import Document


@dataclass
class GlossaryEntry:
    """
    A class to represent a glossary entry.
    """

    signature: str
    """ The signature of the predicate. """
    description: str
    """ The description of the predicate. """
    parameters: dict[str, str]
    """ The parameters and their descriptions of the predicate. """


@dataclass
class Glossary:
    """
    A class to represent a glossary.
    """

    entries: list[GlossaryEntry]
    """ The entries of the glossary. """

    @staticmethod
    def from_document(document: Document) -> Glossary:
        """
        Initialize the glossary from an ASP document.

        Args:
            document: The ASP document.

        Returns:
            The glossary.
        """

        entries: list[GlossaryEntry] = []

        for predicate in document.predicates.values():
            if predicate.documentation is None:
                entry = GlossaryEntry(
                    signature=predicate.signature,
                    description="No description available.",
                    parameters={},
                )
            else:
                entry = GlossaryEntry(
                    signature=predicate.documentation.signature,
                    description=predicate.documentation.description,
                    parameters=predicate.documentation.parameter_descriptions,
                )
            entries.append(entry)

        entries.sort(key=lambda x: x.signature)

        return Glossary(entries)
