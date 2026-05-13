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


def test_get_predicate_info_filter_unused(render_context: Callable[[str], RenderContext]) -> None:
    """Test that unused predicates are filtered out when the option is set."""

    source = """
    %*! only_documented
    This predicate is documented, but not used anywhere.
    *%
    """

    context = render_context(source)

    context.options.predicate_info.include_unused = False

    assert len(context._predicates) == 0


def test_get_predicate_info_filter_undocumented(render_context: Callable[[str], RenderContext]) -> None:
    """Test that hidden predicates are excluded when the option is set."""

    context = render_context(
        """
    output_pred(X) :- input_pred(X).
    internal_calc(X) :- input_pred(X).
    #show output_pred/1.
    """
    )

    context.options.predicate_info.include_undocumented = False

    assert len(context.glossary.predicates) == 0


def test_get_predicate_info_filter_hidden(render_context: Callable[[str], RenderContext]) -> None:
    """Test that hidden predicates are excluded when the option is set."""

    context = render_context(
        """
    output_pred(X) :- input_pred(X).
    internal_calc(X) :- input_pred(X).
    #show output_pred/1.
    """
    )

    context.options.predicate_info.include_hidden = False

    assert len(context.glossary.predicates) == 2


def test_get_predicate_info_with_pools(render_context: Callable[[str], RenderContext]) -> None:
    """Test that predicates with pools are handled correctly."""

    context = render_context(
        """
    some_predicate(a,b;c,d,e).
    """
    )

    context.options.predicate_info.include_hidden = True

    predicate_info = context._predicates[0]
    assert predicate_info.signature == "some_predicate/2"
    predicate_info = context._predicates[1]
    assert predicate_info.signature == "some_predicate/3"
