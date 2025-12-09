"""This module prepares useful encoding information for rendering."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import cached_property
from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.domain import Document, ShowStatus, Statement

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
class PredicateTableContext:
    predicates: list[PredicateInfo]

@dataclass
class DependencyGraphContext:
    positives: list[tuple[str, str]] = field(default_factory=list)
    negatives: list[tuple[str, str]] = field(default_factory=list)
    all: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    auxiliaries: list[str] = field(default_factory=list)
    inputs: list[str] = field(default_factory=list)


class BlockType(Enum):
    CODE = auto()
    MARKDOWN = auto()

@dataclass
class EncodingBlock:
    type: BlockType
    content: str

@dataclass
class EncodingInfo:
    path: str
    source: str
    blocks: list[EncodingBlock] = field(default_factory=list)

@dataclass
class RenderContext:
    options: ASPOptions
    _predicates: list[PredicateInfo] = field(default_factory=list)
    _encodings: list[EncodingInfo] = field(default_factory=list)

    @cached_property
    def predicate_table(self) -> PredicateTableContext:
        predicates: list[PredicateInfo] = []

        for predicate in self._predicates:
            is_hidden = predicate.show_status == ShowStatus.HIDDEN
            is_undocumented = not predicate.description

            allow_hidden = predicate.is_input or self.options.predicate_table.include_hidden
            allow_undocumented = self.options.predicate_table.include_undocumented

            if (not is_hidden or allow_hidden) and (not is_undocumented or allow_undocumented):
                predicates.append(predicate)

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

        predicates.sort(key=get_sort_priority)

        return PredicateTableContext(predicates=predicates)

    @cached_property
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
    
    @cached_property
    def encodings(self) -> list[EncodingInfo]:
        return self._encodings
        

def get_render_context(documents: list[Document], options: ASPOptions) -> RenderContext:
    
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

    encodings = []

    for document in documents:
        ordered_elements = document.statements + document.line_comments + document.block_comments
        ordered_elements.sort(key=lambda element: element.row)

        encoding = EncodingInfo(path=str(document.path), source=document.content)

        current_block_content = ""
        current_block_type = BlockType.MARKDOWN

        for element in ordered_elements:
            if isinstance(element, Statement):
                if current_block_type != BlockType.CODE:
                    if current_block_content:
                        encoding.blocks.append(
                            EncodingBlock(
                                type=current_block_type,
                                content=current_block_content,
                            )
                        )
                    current_block_content = ""
                    current_block_type = BlockType.CODE

                current_block_content += element.content + "\n"
            
            else:
                if current_block_type != BlockType.MARKDOWN:
                    if current_block_content:
                        encoding.blocks.append(
                            EncodingBlock(
                                type=current_block_type,
                                content=current_block_content,
                            )
                        )
                    current_block_content = ""
                    current_block_type = BlockType.MARKDOWN

                current_block_content += element.content + "\n"
        
        if current_block_content:
            encoding.blocks.append(
                EncodingBlock(
                    type=current_block_type,
                    content=current_block_content,
                )
            )
        
        encodings.append(encoding)


    return RenderContext(options=options, _predicates=list(registry.values()), _encodings=encodings)