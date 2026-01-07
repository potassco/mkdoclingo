"""This module contains common pytest fixtures for tests."""

from pathlib import Path
from typing import Callable

import pytest
from tree_sitter import Parser, Tree

from mkdocstrings_handlers.asp._internal.collect.load import load_documents
from mkdocstrings_handlers.asp._internal.collect.syntax import get_parser
from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.render.render_context import RenderContext


@pytest.fixture(name="parser", scope="session")
def parser_fixture() -> Parser:
    """
    Session-scoped parser.
    Initialized only once for the entire test suite run. Fast!
    """
    return get_parser()


@pytest.fixture
def parse_to_tree(parser: Parser) -> Callable[[str], Tree]:
    """Helper to parse a string directly into a Tree-sitter tree."""

    def _parse(code: str) -> Tree:
        return parser.parse(bytes(code, "utf8"))

    return _parse


@pytest.fixture
def render_context(tmp_path: Path) -> Callable[[str], RenderContext]:
    """Helper to create a RenderContext from given file content."""

    def _render_context(file_content: str) -> RenderContext:
        file_path = tmp_path / "test.lp"
        file_path.write_text(file_content, encoding="utf-8")
        documents = load_documents([file_path])
        options = ASPOptions()
        return RenderContext(documents=documents, options=options)

    return _render_context
