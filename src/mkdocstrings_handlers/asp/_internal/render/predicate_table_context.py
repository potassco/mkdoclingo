from dataclasses import dataclass

from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.domain import ShowStatus
from mkdocstrings_handlers.asp._internal.render.predicate_info import PredicateInfo


@dataclass
class PredicateTableContext:
    predicates: list[PredicateInfo]


def get_predicate_table_context(predicates: list[PredicateInfo], options: ASPOptions) -> PredicateTableContext:
    result: list[PredicateInfo] = []

    for predicate in predicates:
        is_hidden = predicate.show_status == ShowStatus.HIDDEN
        is_undocumented = not predicate.description

        allow_hidden = predicate.is_input or options.predicate_table.include_hidden
        allow_undocumented = options.predicate_table.include_undocumented

        if (not is_hidden or allow_hidden) and (not is_undocumented or allow_undocumented):
            result.append(predicate)

    def get_sort_priority(predicate: PredicateInfo) -> tuple[int, str]:
        is_input = predicate.is_input
        is_hidden = predicate.show_status == ShowStatus.HIDDEN

        match (is_input, is_hidden):
            case (True, False):
                return (0, predicate.signature)
            case (True, True):
                return (1, predicate.signature)
            case (False, False):
                return (2, predicate.signature)
            case (False, True):
                return (3, predicate.signature)

    result.sort(key=get_sort_priority)

    return PredicateTableContext(predicates=result)
