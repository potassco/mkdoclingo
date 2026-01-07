"""
This module defines the main RenderContext dataclass containing various sub contexts.

These sub contexts provide structured information for rendering different parts of the ASP documentation,
such as predicate tables, dependency graphs, encodings, and glossaries.
"""

from __future__ import annotations

from functools import cached_property

from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.domain import Document
from mkdocstrings_handlers.asp._internal.render.dependency_graph_context import (
    DependencyGraphContext,
    get_dependency_graph_context,
)
from mkdocstrings_handlers.asp._internal.render.encodings_context import EncodingContext, get_encoding_context
from mkdocstrings_handlers.asp._internal.render.glossary_context import GlossaryContext, get_glossary_context
from mkdocstrings_handlers.asp._internal.render.predicate_info import PredicateInfo, get_predicate_infos
from mkdocstrings_handlers.asp._internal.render.predicate_table_context import (
    PredicateTableContext,
    get_predicate_table_context,
)


class RenderContext:
    """Dataclass containing various rendering contexts for ASP documentation."""

    def __init__(self, documents: list[Document], options: ASPOptions) -> None:
        """
        Initialize the render context.

        Args:
            documents: The list of collected ASP documents (stored internally).
            options: The ASP handler options.
        """
        self.options = options
        self._documents = documents

    @cached_property
    def _predicates(self) -> list[PredicateInfo]:
        """
        Extract PredicateInfo objects from the documents.

        This is private in order to discourage logic in templates from accessing it directly.
        Instead, the logic should be encapsulated in the specific contexts.
        """

        return get_predicate_infos(self._documents)

    @cached_property
    def predicate_table(self) -> PredicateTableContext:
        """Get the predicate table context."""

        return get_predicate_table_context(self._predicates, self.options)

    @cached_property
    def dependency_graph(self) -> DependencyGraphContext:
        """Get the dependency graph context."""

        return get_dependency_graph_context(self._predicates)

    @cached_property
    def encodings(self) -> EncodingContext:
        """Get the encoding context."""

        return get_encoding_context(self._documents, self.options)

    @cached_property
    def glossary(self) -> GlossaryContext:
        """Get the glossary context."""

        return get_glossary_context(self._predicates, self.options)
