from dataclasses import dataclass, field
from mkdocstrings_handlers.asp._internal.domain import ShowStatus
from mkdocstrings_handlers.asp._internal.render.predicate_info import PredicateInfo

@dataclass
class DependencyGraphContext:
    positives: list[tuple[str, str]] = field(default_factory=list)
    negatives: list[tuple[str, str]] = field(default_factory=list)
    all: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    auxiliaries: list[str] = field(default_factory=list)
    inputs: list[str] = field(default_factory=list)

def get_dependency_graph_context(predicates: list[PredicateInfo]) -> DependencyGraphContext:
    positives = []
    negatives = []
    outputs = []
    auxiliaries = []
    inputs = []

    for predicate in predicates:
        if predicate.is_input:
            inputs.append(predicate.signature)
        
        if predicate.show_status != ShowStatus.HIDDEN:
            outputs.append(predicate.signature)
        else:
            auxiliaries.append(predicate.signature)

        for dep in predicate.positive_dependencies:
            positives.append((dep, predicate.signature))
        for dep in predicate.negative_dependencies:
            negatives.append((dep, predicate.signature))

    all_preds = [predicate.signature for predicate in predicates]

    return DependencyGraphContext(
        positives=positives,
        negatives=negatives,
        all=all_preds,
        outputs=outputs,
        auxiliaries=auxiliaries,
        inputs=inputs,
    )