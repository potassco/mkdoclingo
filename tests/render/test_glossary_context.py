"""This module contains tests for the glossary context used for rendering."""

from typing import Callable

from mkdocstrings_handlers.asp._internal.render.render_context import RenderContext


def test_get_glossary_context_sorting(render_context: Callable[[str], RenderContext]) -> None:
    """Test that the glossary context is built correctly."""

    source = """
    output_pred(X) :- shown_input_pred(X).
    internal_calc(X) :- hidden_input_pred(X).
    #show output_pred/1.
    #show shown_input_pred/1.
    """

    context = render_context(source)

    assert len(context.glossary.predicates) == 4
    sorted_signatures = [pred.info.signature for pred in context.glossary.predicates]

    expected_order = ["shown_input_pred/1", "hidden_input_pred/1", "output_pred/1", "internal_calc/1"]
    assert sorted_signatures == expected_order


def test_get_glossary_context_multiple_reference(render_context: Callable[[str], RenderContext]) -> None:
    """
    Test that multiple references to the same predicate in the same row are handled correctly.

    Namely, if multiple references occur on the same line, only one GlossaryReference should be created for that line.
    """

    source = """
    p(X+Y) :- q(X), q(Y).
    """

    context = render_context(source)

    assert len(context.glossary.predicates) == 2


def test_get_glossary_context_not_show_undocumented(render_context: Callable[[str], RenderContext]) -> None:
    """Test that hidden predicates are excluded when the option is set."""

    context = render_context(
        """
    output_pred(X) :- input_pred(X).
    internal_calc(X) :- input_pred(X).
    #show output_pred/1.
    """
    )

    context.options.glossary.include_undocumented = False

    assert len(context.glossary.predicates) == 0
