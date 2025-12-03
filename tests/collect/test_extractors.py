from typing import Callable

from tree_sitter import Tree

from mkdocstrings_handlers.asp._internal.collect.debug import print_tree
from mkdocstrings_handlers.asp._internal.collect.extractors import extract_include, extract_predicate


def test_extract_include(tmp_path, parse_string: Callable[[str], Tree]):
    """Test extracting an Include from an include node."""

    parent_file = tmp_path / "main.lp"

    include_path = tmp_path / "includes"
    include_path.mkdir()

    included_file = include_path / "some_file.lp"
    included_file.touch()

    source = '#include "includes/some_file.lp".'
    tree = parse_string(source)

    include_node = tree.root_node.child(0)
    include = extract_include(include_node, parent_file_path=parent_file)

    assert include.path == included_file


def test_extract_predicate(parse_string: Callable[[str], Tree]) -> None:
    source = 'p(X, Y, 1, 2,"a string").'
    tree = parse_string(source)

    rule_node = tree.root_node.child(0)
    literal_node = rule_node.child(0)
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "p"
    assert predicate.arity == 5
    assert predicate.negation == False


def test_extract_predicate_without_terms(parse_string: Callable[[str], Tree]) -> None:
    source = "p."
    tree = parse_string(source)

    rule_node = tree.root_node.child(0)
    literal_node = rule_node.child(0)
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "p"
    assert predicate.arity == 0
    assert predicate.negation == False


def test_extract_predicate_negative(parse_string: Callable[[str], Tree]) -> None:
    source = "not p(X, Y)."
    tree = parse_string(source)
    print_tree(tree.root_node, bytes(source, "utf8"), depth=1)
    rule_node = tree.root_node.child(0)
    literal_node = rule_node.child(0)
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "p"
    assert predicate.arity == 2
    assert predicate.negation == True


def test_extract_predicate_from_body_literal(parse_string: Callable[[str], Tree]) -> None:
    source = ":- not q(Y, Z)."
    tree = parse_string(source)
    print_tree(tree.root_node, bytes(source, "utf8"), depth=2)
    rule_node = tree.root_node.child(0)
    body_node = rule_node.child_by_field_name("body")
    literal_node = body_node.child(0)
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "q"
    assert predicate.arity == 2
    assert predicate.negation == True
