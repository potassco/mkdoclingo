from dataclasses import dataclass, field
from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.domain import ShowStatus
from mkdocstrings_handlers.asp._internal.render.predicate_info import PredicateInfo

@dataclass
class GlossaryContext:
    predicates: list[PredicateInfo] = field(default_factory=list)

def get_glossary_context(predicates: list[PredicateInfo], options:ASPOptions) -> GlossaryContext:
    result: list[PredicateInfo] = []

    for predicate in predicates:
        is_hidden = predicate.show_status == ShowStatus.HIDDEN
        is_undocumented = not predicate.description

        allow_hidden = predicate.is_input or options.glossary.include_hidden
        allow_undocumented = options.glossary.include_undocumented

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

    return GlossaryContext(predicates=result)