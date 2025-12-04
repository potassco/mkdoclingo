from typing import Callable

from tree_sitter import Tree

from mkdocstrings_handlers.asp._internal.collect.debug import print_tree
from mkdocstrings_handlers.asp._internal.collect.extractors import (
    extract_block_comment,
    extract_include,
    extract_line_comment,
    extract_predicate,
    extract_statement,
)


def test_extract_include(tmp_path, parse_to_tree: Callable[[str], Tree]):
    """Test extracting an Include from an include node."""

    parent_file = tmp_path / "main.lp"

    include_path = tmp_path / "includes"
    include_path.mkdir()

    included_file = include_path / "some_file.lp"
    included_file.touch()

    source = '#include "includes/some_file.lp".'
    tree = parse_to_tree(source)

    include_node = tree.root_node.child(0)
    include = extract_include(include_node, parent_file_path=parent_file)

    assert include.path == included_file


def test_extract_predicate(parse_to_tree: Callable[[str], Tree]) -> None:
    source = 'p(X, Y, 1, 2,"a string").'
    tree = parse_to_tree(source)

    rule_node = tree.root_node.child(0)
    literal_node = rule_node.child(0)
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "p"
    assert predicate.arity == 5
    assert predicate.negation == False


def test_extract_predicate_without_terms(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "p."
    tree = parse_to_tree(source)

    rule_node = tree.root_node.child(0)
    literal_node = rule_node.child(0)
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "p"
    assert predicate.arity == 0
    assert predicate.negation == False


def test_extract_predicate_negative(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "not p(X, Y)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    literal_node = rule_node.child(0)
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "p"
    assert predicate.arity == 2
    assert predicate.negation == True


def test_extract_predicate_from_body_literal(parse_to_tree: Callable[[str], Tree]) -> None:
    source = ":- not q(Y, Z)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    body_node = rule_node.child_by_field_name("body")
    literal_node = body_node.child(0)
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "q"
    assert predicate.arity == 2
    assert predicate.negation == True


def test_extract_line_comment(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "% This is a comment"
    tree = parse_to_tree(source)
    comment_node = tree.root_node.child(0)
    print_tree(tree.root_node, source, 0)
    line_comment = extract_line_comment(comment_node)

    assert line_comment.row == 0
    assert line_comment.content == " This is a comment"


def test_extract_block_comment(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "%* This\n is\n a\n block\n comment.*%"
    tree = parse_to_tree(source)
    comment_node = tree.root_node.child(0)
    print_tree(tree.root_node, source, 0)
    block_comment = extract_block_comment(comment_node)

    assert block_comment.row == 0
    assert block_comment.content == " This\n is\n a\n block\n comment."


def test_extract_statement_head_literal(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "p(1)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 0


def test_extract_statement_head_disjunction(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "p(1); q(2)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 2
    assert len(statement.needed_predicates) == 0


def test_extract_statement_head_conditional(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "p(1):q, not r(2)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_body(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "p(X) :- q(X), not r(X)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_body_aggregate(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "p(X) :- X = #count { Y : q(Y), not r(Y) } > 2."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_body_set_aggregate(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "p :- 0 < { q(Y) : not r(Y) }."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_head_aggregate(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "0 <#sum {X:p(X):q(X)}."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 1


def test_extract_statement_with_head_set_aggregate(parse_to_tree: Callable[[str], Tree]) -> None:
    source = "1{p(X):q(X)}."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 1


def test_extract_statement_with_comparison(parse_to_tree: Callable[[str], Tree]) -> None:
    source = ":- q(X), r(Y), X!=Y."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    print_tree(tree.root_node, source, 0)
    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 0
    assert len(statement.needed_predicates) == 2
