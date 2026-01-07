"""This module contains tests for the debug printing of syntax trees."""

import re
from typing import Callable

from pytest import CaptureFixture
from tree_sitter import Tree

from mkdocstrings_handlers.asp._internal.collect.debug import print_tree


def test_print_tree_structure(parse_to_tree: Callable[[str], Tree], capsys: CaptureFixture[str]) -> None:
    """Test the `print_tree` function to ensure it correctly prints the structure."""

    source = "a(1,2)."
    tree = parse_to_tree(source)

    print_tree(tree.root_node, source.encode("utf8"), 0)
    captured = capsys.readouterr()
    output_lines = captured.out.splitlines()

    # Since node ids are not stable between calls, we have to account for that
    assert re.search(r"^source_file \d+:", output_lines[0])
    assert re.search(r"^\s+rule \d+: a\(1,2\)\.", output_lines[1])
    assert re.search(r"^\s+literal \d+: a\(1,2\)", output_lines[2])
    assert re.search(r"number \d+: 1", output_lines[7])
    assert re.search(r"number \d+: 2", output_lines[9])
