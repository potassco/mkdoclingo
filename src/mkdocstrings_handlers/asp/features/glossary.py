from __future__ import annotations

from dataclasses import dataclass

from mkdocstrings_handlers.asp.document import Document
from mkdocstrings_handlers.asp.semantics.predicate_documentation import PredicateDocumentation


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

        for predicate_documentation in document.predicate_documentations:
            entry = GlossaryEntry(
                signature=predicate_documentation.literal.text,
                description=predicate_documentation.description,
                parameters=predicate_documentation.parameter_descriptions,
            )
            entries.append(entry)

        entries.sort(key=lambda x: x.signature)

        return Glossary(entries)
