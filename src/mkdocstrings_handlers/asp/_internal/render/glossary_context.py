"""This module defines the glossary context for rendering."""

from dataclasses import dataclass, field

from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.domain import ShowStatus
from mkdocstrings_handlers.asp._internal.render.predicate_info import PredicateInfo


@dataclass
class GlossaryReference:
    """Represents a single reference to a predicate in a file."""

    row: int
    """ The row number of the reference in the file. """
    content: str
    """ The content of the line where the reference is found. """
    is_providing: bool
    """ Whether this reference is a definition (providing) or just a usage (not providing). """


@dataclass
class FileReference:
    """Represents one file tab in the glossary."""

    path: str
    """ The path to the file. """
    references: list[GlossaryReference] = field(default_factory=list)
    """ References found in this file. """


@dataclass
class GlossaryPredicate:
    """A predicate entry in the glossary with pre-grouped references."""

    info: PredicateInfo
    """ The predicate information. """
    files: list[FileReference]
    """ Files containing references for this predicate. """


@dataclass
class GlossaryContext:
    """The glossary context containing all glossary predicates."""

    predicates: list[GlossaryPredicate] = field(default_factory=list)
    """ The list of glossary predicates. """


def _add_reference_to_map(
    file_row_map: dict[str, dict[int, GlossaryReference]],
    path: str,
    row: int,
    content: str,
    is_providing: bool,
) -> None:
    """
    Helper to add a reference to the map, avoiding duplicates.
    Moved outside to avoid Pylint W0640 (cell-var-from-loop).
    """
    if path not in file_row_map:
        file_row_map[path] = {}

    if row not in file_row_map[path]:
        file_row_map[path][row] = GlossaryReference(row=row, content=content, is_providing=is_providing)


def get_glossary_context(predicates: list[PredicateInfo], options: ASPOptions) -> GlossaryContext:
    """
    Build the glossary context from the given predicates and options.

    Args:
        predicates: The list of PredicateInfo objects to include in the glossary.
        options: The ASPOptions containing glossary display settings.

    Returns:
        The constructed GlossaryContext.
    """
    result: list[GlossaryPredicate] = []

    for predicate in predicates:
        is_hidden = predicate.show_status == ShowStatus.HIDDEN
        is_undocumented = not predicate.description

        allow_hidden = predicate.is_input or options.glossary.include_hidden
        allow_undocumented = options.glossary.include_undocumented

        should_show = (not is_hidden or allow_hidden) and (not is_undocumented or allow_undocumented)

        if not should_show:
            continue

        file_row_map: dict[str, dict[int, GlossaryReference]] = {}

        for definition in predicate.definitions:
            _add_reference_to_map(file_row_map, definition.path, definition.row, definition.content, True)

        for reference in predicate.references:
            _add_reference_to_map(file_row_map, reference.path, reference.row, reference.content, False)

        file_references = []
        for path, row_map in file_row_map.items():
            references = list(row_map.values())
            references.sort(key=lambda ref: ref.row)

            file_references.append(FileReference(path=path, references=references))

        file_references.sort(key=lambda file: file.path)

        result.append(
            GlossaryPredicate(
                info=predicate,
                files=file_references,
            )
        )

    def get_sort_priority(predicate: GlossaryPredicate) -> tuple[int, str]:
        """
        Determine the sort priority for a glossary predicate.

        Args:
            predicate: The GlossaryPredicate to evaluate.

        Returns:
            A tuple representing the sort priority.
        """
        is_input = predicate.info.is_input
        is_hidden = predicate.info.show_status == ShowStatus.HIDDEN
        signature = predicate.info.signature

        match (is_input, is_hidden):
            case (True, False):
                return (0, signature)
            case (True, True):
                return (1, signature)
            case (False, False):
                return (2, signature)
            case _:
                return (3, signature)

    result.sort(key=get_sort_priority)

    return GlossaryContext(predicates=result)
