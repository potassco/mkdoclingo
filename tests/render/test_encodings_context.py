"""This module contains tests for the encodings context rendering."""

from typing import Callable

from mkdocstrings_handlers.asp._internal.render.render_context import RenderContext


def test_get_encodings_context(render_context: Callable[[str], RenderContext]) -> None:
    """Test that the encodings context is built correctly."""

    source = """
    output_pred(X) :- shown_input_pred(X).
    internal_calc(X) :- hidden_input_pred(X).
    #show output_pred/1.
    #show shown_input_pred/1.
    """

    context = render_context(source)

    assert len(context.encodings.entries) == 1
    encoding_info = context.encodings.entries[0]
    assert encoding_info.source.splitlines() == source.splitlines()
    assert len(encoding_info.blocks) == 1


def test_get_encodings_context_with_comments(render_context: Callable[[str], RenderContext]) -> None:
    """Test that the encodings context is built correctly with comments."""

    source = """
    % rules
    output_pred(X) :- shown_input_pred(X).
    internal_calc(X) :- hidden_input_pred(X).
    % show statements
    #show output_pred/1.
    #show shown_input_pred/1.
    """

    context = render_context(source)

    assert len(context.encodings.entries) == 1
    encoding_info = context.encodings.entries[0]
    assert encoding_info.source.splitlines() == source.splitlines()
    assert len(encoding_info.blocks) == 4
