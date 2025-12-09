"""This module builds the context for rendering predicate tables."""

from dataclasses import dataclass

from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.domain import ShowStatus
from mkdocstrings_handlers.asp._internal.render.predicate_info import PredicateInfo


@dataclass
class PredicateTableContext:
    """The context for rendering a predicate table."""

    predicates: list[PredicateInfo]
    """ The list of predicates to include in the table. """


def get_predicate_table_context(predicates: list[PredicateInfo], options: ASPOptions) -> PredicateTableContext:
    """
    Build the predicate table context from the given predicates and options.

    Args:
        predicates: The list of PredicateInfo objects to include in the predicate table.
        options: The ASPOptions containing predicate table display settings.

    Returns:
        The constructed PredicateTableContext.
    """
    result: list[PredicateInfo] = []

    for predicate in predicates:
        is_hidden = predicate.show_status == ShowStatus.HIDDEN
        is_undocumented = not predicate.description

        allow_hidden = predicate.is_input or options.predicate_table.include_hidden
        allow_undocumented = options.predicate_table.include_undocumented

        if (not is_hidden or allow_hidden) and (not is_undocumented or allow_undocumented):
            result.append(predicate)

    def get_sort_priority(predicate: PredicateInfo) -> tuple[int, str]:
        """
        Get the sort priority for a predicate.

        The sorting priority is determined by whether the predicate is an input predicate and whether it is hidden.

        Args:
            predicate: The PredicateInfo object to get the sort priority for.

        Returns:
            A tuple representing the sort priority.
        """
        is_input = predicate.is_input
        is_hidden = predicate.show_status == ShowStatus.HIDDEN

        match (is_input, is_hidden):
            case (True, False):
                return (0, predicate.signature)
            case (True, True):
                return (1, predicate.signature)
            case (False, False):
                return (2, predicate.signature)
            case _:
                return (3, predicate.signature)

    result.sort(key=get_sort_priority)

    return PredicateTableContext(predicates=result)
