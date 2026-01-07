"""This module contains tests for the ASPHandler"""

# pylint: disable=protected-access

from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch
from xml.etree.ElementTree import Element

import pytest
from markdown import Markdown
from mkdocstrings import HeadingShiftingTreeprocessor

from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.domain import Document
from mkdocstrings_handlers.asp._internal.handler import ASPHandler, get_handler


@pytest.fixture(name="asp_handler")
def asp_handler_fixture() -> ASPHandler:
    """Fixture that provides an ASPHandler instance."""

    return get_handler(
        theme="material", custom_templates=None, mdx=[], mdx_config={}, tool_config={}, handler_config={}
    )


def test_handler_get_options(asp_handler: ASPHandler) -> None:
    """Test that get_options returns correct default options."""

    options = asp_handler.get_options({})
    assert options.predicate_table.include_hidden is True
    assert options.predicate_table.include_undocumented is True
    assert options.glossary.include_hidden is True
    assert options.glossary.include_undocumented is True


def test_handler_get_options_merge_handler_config(asp_handler: ASPHandler) -> None:
    """Test that get_options merges handler_config with local options.

    The local options should override handler_config where specified,
    while other settings should be preserved from handler_config.
    """

    asp_handler._handler_config = {
        "options": {
            "predicate_table": {
                "include_hidden": False,
                "include_undocumented": True,
            },
            "glossary": {
                "include_undocumented": False,
            },
        }
    }

    local_options = {
        "predicate_table": {
            "include_undocumented": False,
        },
        "glossary": {
            "include_hidden": True,
        },
    }

    options = asp_handler.get_options(local_options)

    assert options.predicate_table.include_hidden is False
    assert options.predicate_table.include_undocumented is False
    assert options.glossary.include_hidden is True
    assert options.glossary.include_undocumented is False


def test_handler_get_options_with_repository_url(asp_handler: ASPHandler) -> None:
    """Test that get_options includes repository_url from tool_config."""

    repository_url = "https://example.com/repo"
    asp_handler._tool_config = {"repo_url": repository_url}
    options = asp_handler.get_options({})

    assert options.repo_url == repository_url


def test_handler_collect(asp_handler: ASPHandler) -> None:
    """Test that collect calls load_documents with the correct path and returns the result."""

    identifier = Path("path/to/file.lp")

    with patch("mkdocstrings_handlers.asp._internal.handler.load_documents") as mock_load:
        document = Document(identifier, "some_content.")
        mock_load.return_value = [document]

        result = asp_handler.collect(str(identifier), ASPOptions())

        assert result == [document]
        mock_load.assert_called_once_with([identifier])
        assert result[0].content == "some_content."


def test_handler_update_env(asp_handler: ASPHandler) -> None:
    """Test that the markdown filter is registered."""
    config: dict[str, Any] = {}
    asp_handler.update_env(config)

    assert "convert_markdown_simple" in asp_handler.env.filters
    assert asp_handler.env.filters["convert_markdown_simple"] == asp_handler.do_convert_markdown_simple


def test_render(asp_handler: ASPHandler) -> None:
    """Test that render creates a RenderContext and passes it to the template."""

    mock_template = Mock()
    asp_handler.env = Mock()
    asp_handler.env.get_template.return_value = mock_template

    with patch("mkdocstrings_handlers.asp._internal.handler.RenderContext") as mock_context:
        document = Document(Path("path/to/file.lp"), "some_content.")
        options = ASPOptions()
        asp_handler.render([document], options)
        asp_handler.env.get_template.assert_called_once_with("documentation.html.jinja")
        mock_context.assert_called_once_with(documents=[document], options=options)

        mock_template.render.assert_called_once()
        call_kwargs = mock_template.render.call_args[1]
        assert call_kwargs["context"] == mock_context.return_value


def test_do_convert_markdown_simple_no_md(asp_handler: ASPHandler) -> None:
    """Test error when markdown instance is missing."""
    asp_handler._md = None

    with pytest.raises(RuntimeError, match="Markdown instance is not initialized"):
        asp_handler.do_convert_markdown_simple("text", 1)


def test_do_convert_markdown_simple_success(asp_handler: ASPHandler) -> None:
    """
    Test successful markdown conversion using the provided heading level
    and not affecting existing headings.
    """

    old_heading = Element("h1")
    old_heading.text = "Some existing Heading"
    text = "# Some new Heading"
    heading_level = 2
    # Since the handler doesn't create the _md itself
    # we simulte mkdocstrings inserting it
    md = Markdown()
    processor = HeadingShiftingTreeprocessor(md, 0)
    md.treeprocessors.register(
        processor, HeadingShiftingTreeprocessor.name, 69  # This number is irrelevant for the test
    )
    asp_handler._md = md
    asp_handler._headings = [old_heading]
    result = asp_handler.do_convert_markdown_simple(text, heading_level)

    assert result == "<h3>Some new Heading</h3>"
    assert asp_handler._headings == [old_heading]
    assert processor.shift_by == 0
