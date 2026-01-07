"""This module contains tests for the encodings context rendering."""

# pylint: disable=protected-access
from pathlib import Path
from typing import Callable

import pytest

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


@pytest.mark.parametrize(
    ("repo_url", "file_path", "expected_url"),
    [
        ("https://example.com/repo", "src/file.lp", "https://example.com/repo/tree/master/src/file.lp"),
        ("https://example.com/repo/", "src/file.lp", "https://example.com/repo/tree/master/src/file.lp"),
        ("https://example.com/repo", "/src/file.lp", "https://example.com/repo/tree/master/src/file.lp"),
        ("https://example.com/repo/", "/src/file.lp", "https://example.com/repo/tree/master/src/file.lp"),
        (None, "src/file.lp", None),
        ("https://example.com/repo", "deep/nested/file.lp", "https://example.com/repo/tree/master/deep/nested/file.lp"),
    ],
)
def test_get_encodings_context_contains_repo_url(
    render_context: Callable[[str], RenderContext], repo_url: str | None, file_path: str, expected_url: str
) -> None:
    """Test that the encodings repository link is built correctly."""

    context = render_context("")
    context._documents[0].path = Path(file_path)
    context.options.repo_url = repo_url

    assert len(context.encodings.entries) == 1
    encoding_info = context.encodings.entries[0]
    assert encoding_info.repository_url == expected_url
