from dataclasses import dataclass, field

from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.domain import ShowStatus
from mkdocstrings_handlers.asp._internal.render.predicate_info import PredicateInfo


@dataclass
class GlossaryReference:
    row: int
    content: str
    is_providing: bool


@dataclass
class FileReference:
    """Represents one file tab in the glossary."""

    path: str
    references: list[GlossaryReference] = field(default_factory=list)


@dataclass
class GlossaryPredicate:
    """A predicate entry in the glossary with pre-grouped references."""

    info: PredicateInfo
    files: list[FileReference]


@dataclass
class GlossaryContext:
    predicates: list[GlossaryPredicate] = field(default_factory=list)


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

        def add_reference(path: str, row: int, content: str, is_providing: bool) -> None:
            """
            Add a reference to the file_row_map, avoiding duplicates.
            """
            if path not in file_row_map:
                file_row_map[path] = {}

            existing = file_row_map[path].get(row)

            if existing:
                if is_providing and not existing.is_providing:
                    existing.is_providing = True
            else:
                file_row_map[path][row] = GlossaryReference(row=row, content=content, is_providing=is_providing)

        for definition in predicate.definitions:
            add_reference(definition.path, definition.row, definition.content, True)

        for reference in predicate.references:
            add_reference(reference.path, reference.row, reference.content, False)

        file_references = []
        for path, row_map in file_row_map.items():
            references = list(row_map.values())
            references.sort(key=lambda occ: occ.row)

            file_references.append(FileReference(path=path, references=references))

        file_references.sort(key=lambda f: f.path)

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
