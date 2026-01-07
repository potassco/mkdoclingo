"""Module defining the context for rendering dependency graphs."""

from dataclasses import dataclass, field

from mkdocstrings_handlers.asp._internal.domain import ShowStatus
from mkdocstrings_handlers.asp._internal.render.predicate_info import PredicateInfo


@dataclass
class DependencyGraphContext:
    """The context for rendering a dependency graph."""

    positives: list[tuple[str, str]] = field(default_factory=list)
    """ List of positive dependencies as (from, to) tuples. """
    negatives: list[tuple[str, str]] = field(default_factory=list)
    """ List of negative dependencies as (from, to) tuples. """
    all: list[str] = field(default_factory=list)
    """ List of all predicate signatures. """
    outputs: list[str] = field(default_factory=list)
    """ List of output predicate signatures. """
    auxiliaries: list[str] = field(default_factory=list)
    """ List of auxiliary predicate signatures. """
    inputs: list[str] = field(default_factory=list)
    """ List of input predicate signatures. """


def get_dependency_graph_context(predicates: list[PredicateInfo]) -> DependencyGraphContext:
    """
    Build the dependency graph context from the given predicates.

    Args:
        predicates: The list of PredicateInfo objects to include in the dependency graph.

    Returns:
        The constructed DependencyGraphContext.
    """
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
