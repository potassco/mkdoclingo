import string
from dataclasses import dataclass, field

from mkdocstrings_handlers.asp._internal.domain import Document, ShowStatus


@dataclass
class Occurrence:
    path: str
    row: int
    content: str


@dataclass
class ArgumentInfo:
    identifier: str
    description: str


@dataclass
class PredicateInfo:
    signature: str
    description: str = ""
    arguments: list[ArgumentInfo] = field(default_factory=list)
    definitions: list[Occurrence] = field(default_factory=list)
    references: list[Occurrence] = field(default_factory=list)
    positive_dependencies: set[str] = field(default_factory=set)
    negative_dependencies: set[str] = field(default_factory=set)
    show_status: ShowStatus = ShowStatus.DEFAULT
    is_input: bool = True

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


def get_predicate_infos(documents: list[Document]) -> list[PredicateInfo]:

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

    default_show = ShowStatus.DEFAULT

    for document in documents:
        for show in document.shows:
            if show.status == ShowStatus.EXPLICIT:
                default_show = ShowStatus.HIDDEN

            if show.predicate is not None:
                info = get_info(show.predicate.signature)
                info.show_status |= show.status

                if info.show_status > ShowStatus.HIDDEN:
                    info.show_status &= ShowStatus.PARTIAL_AND_EXPLICIT

    for info in registry.values():
        if info.show_status == ShowStatus.DEFAULT:
            info.show_status = default_show

    return list(registry.values())
