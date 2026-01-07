"""This module contains tests for the creation of PredicateInfos."""

# pylint: disable=protected-access

from typing import Callable

from mkdocstrings_handlers.asp._internal.render.render_context import RenderContext


def test_get_predicate_info(render_context: Callable[[str], RenderContext]) -> None:
    """Test that the glossary context is built correctly."""

    source = """
    output_pred(X) :- shown_input_pred(X).
    internal_calc(X) :- hidden_input_pred(X).
    #show output_pred/1.
    #show shown_input_pred/1.
    """

    context = render_context(source)

    assert len(context._predicates) == 4


def test_get_predicate_info_str_representation(render_context: Callable[[str], RenderContext]) -> None:
    """Test the string representation of PredicateInfo."""

    source = """
    some_predicate(1,2,3).
    """

    context = render_context(source)

    assert len(context._predicates) == 1
    assert context._predicates[0].signature == "some_predicate/3"
    assert str(context._predicates[0]) == "some_predicate(A, B, C)"


def test_get_predicate_info_str_representation_with_documentation(
    render_context: Callable[[str], RenderContext],
) -> None:
    """Test the string representation of PredicateInfo with documentation."""

    source = """
    %*! some_predicate(X, Y, Z).
    *%
    some_predicate(1,2,3).
    """

    context = render_context(source)

    assert len(context._predicates) == 1
    predicate_info = context._predicates[0]
    assert predicate_info.signature == "some_predicate/3"
    assert str(predicate_info) == "some_predicate(X, Y, Z)"


def test_get_predicate_info_show_only(render_context: Callable[[str], RenderContext]) -> None:
    """Test that predicate info is created even for standalone show statements."""

    source = """
    #show some_predicate/2.
    """

    context = render_context(source)

    assert len(context._predicates) == 1
    predicate_info = context._predicates[0]
    assert predicate_info.signature == "some_predicate/2"
