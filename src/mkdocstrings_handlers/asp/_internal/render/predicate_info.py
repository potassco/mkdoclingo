"""This module defines the predicate information for rendering."""

import string
from dataclasses import dataclass, field

from mkdocstrings_handlers.asp._internal.domain import Document, ShowStatus


@dataclass
class Occurrence:
    """An occurrence of a predicate in the code."""

    path: str
    """ The path to the file where the occurrence is found. """
    row: int
    """ The row number of the occurrence in the file. """
    content: str
    """ The content of the line where the occurrence is found. """


@dataclass
class ArgumentInfo:
    """Information about a predicate argument."""

    identifier: str
    """ The identifier of the argument. """
    description: str
    """ The description of the argument. """


# pylint: disable=too-many-instance-attributes
@dataclass
class PredicateInfo:
    """Information about a predicate."""

    signature: str
    """ The signature of the predicate, e.g., "parent/2". """
    description: str = ""
    """ The description of the predicate. """
    arguments: list[ArgumentInfo] = field(default_factory=list)
    """ Arguments for the predicate. """
    definitions: list[Occurrence] = field(default_factory=list)
    """
    Definitions of the predicate.

    These are occurrences where the predicate appears in the head of a statement.
    """
    references: list[Occurrence] = field(default_factory=list)
    """
    References to the predicate.

    These are occurrences where the predicate appears in the body of a statement.
    """
    positive_dependencies: set[str] = field(default_factory=set)
    """ The set of signatures of predicates that this predicate positively depends on. """
    negative_dependencies: set[str] = field(default_factory=set)
    """ The set of signatures of predicates that this predicate negatively depends on. """
    show_status: ShowStatus = ShowStatus.DEFAULT
    """ The show status of the predicate. """
    is_input: bool = True
    """ Whether the predicate is an input predicate (i.e., not defined in the code). """

    def __str__(self) -> str:
        """
        Return the string representation of the predicate.

        If the predicate has arguments, their identifiers are used in the representation.
        Otherwise, generic argument names based on the arity are used.

        The default representation is of the form `identifier(A, B, C)` where `A`, `B`, and `C` are
        the first three uppercase letters of the alphabet.

        Returns:
            The string representation of the predicate.
        """
        identifier, arity_str = self.signature.split("/")

        if self.arguments:
            args = ", ".join(arg.identifier for arg in self.arguments)
        else:
            args = ", ".join(string.ascii_uppercase[: int(arity_str)])
        return f"{identifier}({args})"


def _resolve_show_statuses(documents: list[Document], registry: dict[str, PredicateInfo]) -> None:
    """
    Helper function to process #show directives and update predicate statuses.
    Extracting this reduces the branch count of the main function.
    """
    default_show = ShowStatus.DEFAULT

    for document in documents:
        for show in document.shows:
            if show.status == ShowStatus.EXPLICIT:
                default_show = ShowStatus.HIDDEN

            if show.predicate is not None:
                sig = show.predicate.signature
                if sig not in registry:
                    registry[sig] = PredicateInfo(signature=sig)

                info = registry[sig]
                info.show_status = ShowStatus(info.show_status | show.status)

    for info in registry.values():
        if info.show_status == ShowStatus.DEFAULT:
            info.show_status = default_show


def get_predicate_infos(documents: list[Document]) -> list[PredicateInfo]:
    """
    Build the list of PredicateInfo objects from the given documents.

    Args:
        documents: The list of Document objects representing ASP programs.

    Returns:
        The list of constructed PredicateInfo objects.
    """

    registry: dict[str, PredicateInfo] = {}

    def get_info(signature: str) -> PredicateInfo:
        if signature not in registry:
            registry[signature] = PredicateInfo(signature=signature)
        return registry[signature]

    for document in documents:
        for documentation in document.predicate_documentations:
            predicate_info = get_info(documentation.signature)

            predicate_info.description = documentation.description
            predicate_info.arguments = [
                ArgumentInfo(
                    identifier=argument.identifier,
                    description=argument.description,
                )
                for argument in documentation.arguments
            ]

        for statement in document.statements:
            for provided in statement.provided_predicates:
                get_info(provided.signature).definitions.append(
                    Occurrence(
                        path=str(document.path),
                        row=statement.row,
                        content=statement.content,
                    )
                )
                get_info(provided.signature).is_input = False

            for needed in statement.needed_predicates:
                get_info(needed.signature).references.append(
                    Occurrence(
                        path=str(document.path),
                        row=statement.row,
                        content=statement.content,
                    )
                )
            for provided in statement.provided_predicates:
                for needed in statement.needed_predicates:
                    if needed.negation:
                        get_info(provided.signature).negative_dependencies.add(needed.signature)
                    else:
                        get_info(provided.signature).positive_dependencies.add(needed.signature)

    _resolve_show_statuses(documents, registry)

    return list(registry.values())
