"""Tests for the predicate table context generation."""

from typing import Callable

from mkdocstrings_handlers.asp._internal.render.predicate_table_context import get_predicate_table_context
from mkdocstrings_handlers.asp._internal.render.render_context import RenderContext


def test_get_predicate_table_context_sorting(render_context: Callable[[str], RenderContext]) -> None:
    """Test that the predicate table is sorted correctly."""

    context = render_context(
        """
    output_pred(X) :- shown_input_pred(X).
    internal_calc(X) :- hidden_input_pred(X).
    #show output_pred/1.
    #show shown_input_pred/1.
    """
    )

    context.options.predicate_table.include_hidden = True

    table = get_predicate_table_context(context.predicates, context.options)

    sorted_signatures = [pred.signature for pred in table.predicates]

    expected_order = ["shown_input_pred/1", "hidden_input_pred/1", "output_pred/1", "internal_calc/1"]

    assert sorted_signatures == expected_order


def test_get_predicate_table_context_not_show_hidden(render_context: Callable[[str], RenderContext]) -> None:
    """Test that hidden predicates are excluded when the option is set."""

    context = render_context(
        """
    output_pred(X) :- input_pred(X).
    internal_calc(X) :- input_pred(X).
    #show output_pred/1.
    """
    )

    context.options.predicate_table.include_hidden = False
    table = get_predicate_table_context(context.predicates, context.options)

    assert len(table.predicates) == 2


def test_get_predicate_table_context_not_show_undocumented(render_context: Callable[[str], RenderContext]) -> None:
    """Test that hidden predicates are excluded when the option is set."""

    context = render_context(
        """
    output_pred(X) :- input_pred(X).
    internal_calc(X) :- input_pred(X).
    #show output_pred/1.
    """
    )

    context.options.predicate_table.include_undocumented = False
    table = get_predicate_table_context(context.predicates, context.options)

    assert len(table.predicates) == 0
