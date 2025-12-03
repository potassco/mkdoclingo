from typing import Callable

import pytest
from tree_sitter import Parser, Tree

from mkdocstrings_handlers.asp._internal.collect.syntax import get_parser


@pytest.fixture(scope="session")
def parser() -> Parser:
    """
    Session-scoped parser.
    Initialized only once for the entire test suite run. Fast!
    """
    return get_parser()


@pytest.fixture
def parse_string(parser: Parser) -> Callable[[str], Tree]:
    """Helper to parse a string directly into a Tree-sitter tree."""

    def _parse(code: str) -> Tree:
        return parser.parse(bytes(code, "utf8"))

    return _parse
