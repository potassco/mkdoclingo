from typing import Callable

from tree_sitter import Tree

from mkdocstrings_handlers.asp._internal.collect.extractors import (
    extract_include,
    extract_line_comment,
    extract_predicate,
    extract_statement,
)
from mkdocstrings_handlers.asp.tree_sitter.debug import print_tree


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
    rule_node = tree.root_node.child(0)
    literal_node = rule_node.child(0)
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "p"
    assert predicate.arity == 2
    assert predicate.negation == True


def test_extract_predicate_from_body_literal(parse_string: Callable[[str], Tree]) -> None:
    source = ":- not q(Y, Z)."
    tree = parse_string(source)
    rule_node = tree.root_node.child(0)
    body_node = rule_node.child_by_field_name("body")
    literal_node = body_node.child(0)
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "q"
    assert predicate.arity == 2
    assert predicate.negation == True


def test_extract_line_comment(parse_string: Callable[[str], Tree]) -> None:
    source = "% This is a comment"
    tree = parse_string(source)
    comment_node = tree.root_node.child(0)
    print_tree(tree.root_node, source, 0)
    line_comment = extract_line_comment(comment_node)

    assert line_comment.row == 0
    assert line_comment.line == " This is a comment"


def test_extract_statement_head_literal(parse_string: Callable[[str], Tree]) -> None:
    source = "p(1)."
    tree = parse_string(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.text == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 0


def test_extract_statement_head_disjunction(parse_string: Callable[[str], Tree]) -> None:
    source = "p(1); q(2)."
    tree = parse_string(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.text == source
    assert len(statement.provided_predicates) == 2
    assert len(statement.needed_predicates) == 0


def test_extract_statement_head_conditional(parse_string: Callable[[str], Tree]) -> None:
    source = "p(1):q, not r(2)."
    tree = parse_string(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.text == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_body(parse_string: Callable[[str], Tree]) -> None:
    source = "p(X) :- q(X), not r(X)."
    tree = parse_string(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.text == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_body_aggregate(parse_string: Callable[[str], Tree]) -> None:
    source = "p(X) :- X = #count { Y : q(Y), not r(Y) } > 2."
    tree = parse_string(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.text == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_body_set_aggregate(parse_string: Callable[[str], Tree]) -> None:
    source = "p :- 0 < { q(Y) : not r(Y) }."
    tree = parse_string(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.text == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_head_aggregate(parse_string: Callable[[str], Tree]) -> None:
    source = "1{p(X):q(X)}."
    tree = parse_string(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.text == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 1


def test_extract_statement_with_head_set_aggregate1(parse_string: Callable[[str], Tree]) -> None:
    source = "1{p(X):q(X)}."
    tree = parse_string(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.text == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 1


def test_extract_statement_with_head_aggregate2(parse_string: Callable[[str], Tree]) -> None:
    source = "#sum {X:q(X):r(X)}."
    tree = parse_string(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.text == source
    assert len(statement.provided_predicates) == 0
    assert len(statement.needed_predicates) == 2
