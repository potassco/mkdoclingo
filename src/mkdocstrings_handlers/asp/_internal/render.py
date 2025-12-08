"""This module prepares useful encoding information for rendering."""

from __future__ import annotations
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
    signature:str
    description: str = ""
    arguments: list[ArgumentInfo] = field(default_factory=list)
    definitions: list[Occurrence] = field(default_factory=list)
    references: list[Occurrence] = field(default_factory=list)
    positive_dependencies: set[str] = field(default_factory=set)
    negative_dependencies: set[str] = field(default_factory=set)
    show_status: ShowStatus = ShowStatus.DEFAULT
    is_input: bool = True

@dataclass
class DependencyGraphContext:
    positives: list[tuple[str, str]] = field(default_factory=list)
    negatives: list[tuple[str, str]] = field(default_factory=list)
    all: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    auxiliaries: list[str] = field(default_factory=list)
    inputs: list[str] = field(default_factory=list)

@dataclass
class RenderContext:
    _predicates: list[PredicateInfo] = field(default_factory=list)

    @property
    def dependency_graph(self) -> DependencyGraphContext:
        positives = []
        negatives = []
        outputs = []
        auxiliaries = []
        inputs = []

        for predicate in self._predicates:
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

        all_preds = [predicate.signature for predicate in self._predicates]
    
        return DependencyGraphContext(
            positives=positives,
            negatives=negatives,
            all=all_preds,
            outputs=outputs,
            auxiliaries=auxiliaries,
            inputs=inputs,
        )
        

def get_render_context(documents: list[Document]) -> RenderContext:
    
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

    return RenderContext(_predicates=list(registry.values()))