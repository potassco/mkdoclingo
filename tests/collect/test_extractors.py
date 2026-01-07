"""This module tests the extractors for various ASP constructs."""

import re
from pathlib import Path
from typing import Callable, cast
from unittest.mock import Mock

import pytest
from tree_sitter import Node, Tree

from mkdocstrings_handlers.asp._internal.collect.extractors import (
    extract_argument_documentation,
    extract_block_comment,
    extract_include,
    extract_line_comment,
    extract_predicate,
    extract_predicate_documentation,
    extract_show,
    extract_statement,
    get_capture_text,
    get_node_text,
)
from mkdocstrings_handlers.asp._internal.domain import ShowStatus
from mkdocstrings_handlers.asp._internal.error import ExtractionError


def test_get_node_text() -> None:
    """Test getting text from a tree-sitter node."""

    mock_node = Mock()
    mock_node.text = b"some test text"

    assert get_node_text(mock_node) == "some test text"


def test_get_node_text_from_none() -> None:
    """Test getting text from a None node raises ExtractionError."""

    with pytest.raises(ExtractionError, match=re.escape("Expected a node, but got None.")):
        get_node_text(None)


def test_get_node_text_from_node_without_text() -> None:
    """Test getting text from a None node raises ExtractionError."""

    mock_node = Mock()
    mock_node.text = None
    mock_node.type = "test_type"

    with pytest.raises(ExtractionError, match=re.escape("Node test_type exists but has no text content.")):
        get_node_text(mock_node)


def test_get_capture_text() -> None:
    """Test getting text from a capture group."""

    mock_node = Mock()
    mock_node.text = b"captured text"

    captures = {"identifier": [cast(Node, mock_node)]}

    assert get_capture_text(captures, "identifier") == "captured text"


def test_get_capture_text_out_of_bounds() -> None:
    """Test getting text from a capture group."""

    mock_node = Mock()
    mock_node.text = b"captured text"

    captures = {"identifier": [cast(Node, mock_node)]}

    with pytest.raises(
        ExtractionError, match=re.escape("Capture group 'identifier' does not have an element at index 1.")
    ):
        get_capture_text(captures, "identifier", index=1)


def test_get_capture_text_missing_group() -> None:
    """Test getting text from a missing capture group."""

    captures: dict[str, list[Node]] = {}

    with pytest.raises(ExtractionError, match=re.escape("Required capture group 'identifier' is missing or empty.")):
        get_capture_text(captures, "identifier")


def test_extract_include(tmp_path: Path, parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting an Include from an include node."""

    parent_file = tmp_path / "main.lp"

    include_path = tmp_path / "includes"
    include_path.mkdir()

    included_file = include_path / "some_file.lp"
    included_file.touch()

    source = '#include "includes/some_file.lp".'
    tree = parse_to_tree(source)

    include_node = tree.root_node.child(0)
    assert include_node is not None

    include = extract_include(include_node, parent_file_path=parent_file)

    assert include.path == included_file


def test_extract_predicate(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Predicate from a literal node."""

    source = 'p(X, Y, 1, 2,"a string").'
    tree = parse_to_tree(source)

    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    literal_node = rule_node.child(0)
    assert literal_node is not None

    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "p"
    assert predicate.arity == 5
    assert predicate.negation is False


def test_extract_predicate_without_terms(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Predicate with zero arity from a literal node."""

    source = "p."
    tree = parse_to_tree(source)

    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    literal_node = rule_node.child(0)
    assert literal_node is not None
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "p"
    assert predicate.arity == 0
    assert predicate.negation is False


def test_extract_predicate_negative(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a negated Predicate from a literal node."""

    source = "not p(X, Y)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    literal_node = rule_node.child(0)
    assert literal_node is not None
    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "p"
    assert predicate.arity == 2
    assert predicate.negation is True


def test_extract_predicate_from_body_literal(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Predicate from a body literal node."""

    source = ":- not q(Y, Z)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    body_node = rule_node.child_by_field_name("body")
    assert body_node is not None

    literal_node = body_node.child(0)
    assert literal_node is not None

    predicate = extract_predicate(literal_node)

    assert predicate.identifier == "q"
    assert predicate.arity == 2
    assert predicate.negation is True


def test_extract_line_comment(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a LineComment from a line comment node."""

    source = "% This is a comment"
    tree = parse_to_tree(source)
    comment_node = tree.root_node.child(0)
    assert comment_node is not None

    line_comment = extract_line_comment(comment_node)

    assert line_comment.row == 0
    assert line_comment.content == " This is a comment"


def test_extract_block_comment(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a BlockComment from a block comment node."""

    source = "%* This\n is\n a\n block\n comment.*%"
    tree = parse_to_tree(source)
    comment_node = tree.root_node.child(0)
    assert comment_node is not None

    block_comment = extract_block_comment(comment_node)

    assert block_comment.row == 0
    assert block_comment.content == " This\n is\n a\n block\n comment."


def test_extract_show_empty(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Show directive without a predicate."""

    source = "#show ."
    tree = parse_to_tree(source)
    show_node = tree.root_node.child(0)
    assert show_node is not None

    show = extract_show(show_node)

    assert show.predicate is None
    assert show.status == ShowStatus.EXPLICIT


def test_extract_show_signature(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Show directive with a predicate signature."""

    source = "#show p/2."
    tree = parse_to_tree(source)
    show_node = tree.root_node.child(0)
    assert show_node is not None

    show = extract_show(show_node)

    assert show.predicate is not None
    assert show.predicate.identifier == "p"
    assert show.predicate.arity == 2
    assert show.status == ShowStatus.EXPLICIT


def test_extract_show_term_function(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Show directive with a predicate term (function)."""

    source = "#show p(1,2)."
    tree = parse_to_tree(source)
    show_node = tree.root_node.child(0)
    assert show_node is not None

    show = extract_show(show_node)

    assert show.predicate is not None
    assert show.predicate.identifier == "p"
    assert show.predicate.arity == 2
    assert show.status == ShowStatus.PARTIAL


def test_extract_statement_head_literal(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with a single head literal and no body."""

    source = "p(1)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 0


def test_extract_statement_head_disjunction(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with a disjunction in the head and no body."""

    source = "p(1); q(2)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 2
    assert len(statement.needed_predicates) == 0


def test_extract_statement_head_conditional(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with a conditional literal in the head and no body."""

    source = "p(1):q, not r(2)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_body(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with both head and body literals."""

    source = "p(X) :- q(X), not r(X)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_body_aggregate(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with an aggregate in the body."""

    source = "p(X) :- X = #count { Y : q(Y), not r(Y) } > 2."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_body_set_aggregate(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with a set aggregate in the body."""

    source = "p :- 0 < { q(Y) : not r(Y) }."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_head_aggregate(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with an aggregate in the head."""

    source = "0 <#sum {X:p(X):q(X)}."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 1


def test_extract_statement_with_head_set_aggregate(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with a set aggregate in the head."""

    source = "1{p(X):q(X)}."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 1


def test_extract_statement_with_head_set_aggregate_and_body(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with a set aggregate in the head and a body."""

    source = "1{p(X):q(X)} :- r(X)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 2


def test_extract_statement_with_head_set_aggregate_with_comparison(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with a set aggregate with comparison in the head."""

    source = "{ p(V) : V = Min..Max } = 1 :- q(Min,Max)."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 1
    assert len(statement.needed_predicates) == 1


def test_extract_statement_with_comparison(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting a Statement with a comparison in the body."""

    source = ":- q(X), r(Y), X!=Y."
    tree = parse_to_tree(source)
    rule_node = tree.root_node.child(0)
    assert rule_node is not None

    statement = extract_statement(rule_node)

    assert statement.row == 0
    assert statement.content == source
    assert len(statement.provided_predicates) == 0
    assert len(statement.needed_predicates) == 2


def test_extract_argument_documentation(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting ArgumentDocumentation from an argument documentation node."""

    source = """
    %*! some_predicate(X,Y)
    Args:
        - X: first argument
    *%"""
    tree = parse_to_tree(source)
    doc_comment_node = tree.root_node.child(0)
    assert doc_comment_node is not None

    arguments_node = doc_comment_node.child(2)
    assert arguments_node is not None

    argument_node = arguments_node.child(1)
    assert argument_node is not None

    documentation = extract_argument_documentation(argument_node)

    assert documentation.identifier == "X"
    assert documentation.description == "first argument"


def test_extract_argument_documentation_description_missing(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting ArgumentDocumentation when description is missing."""

    source = """
    %*! some_predicate(X,Y)
    Args:
        - X:
    *%"""
    tree = parse_to_tree(source)
    doc_comment_node = tree.root_node.child(0)
    assert doc_comment_node is not None

    arguments_node = doc_comment_node.child(2)
    assert arguments_node is not None

    argument_node = arguments_node.child(1)
    assert argument_node is not None
    documentation = extract_argument_documentation(argument_node)
    assert documentation.identifier == "X"
    assert documentation.description == ""


def test_extract_predicate_documentation(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting PredicateDocumentation from a predicate documentation node."""

    source = """
    %*! some_predicate(X,Y)
    This is some predicate description.
    Args:
        - X: first argument
        - Y: second argument
    *%"""

    tree = parse_to_tree(source)
    comment_node = tree.root_node.child(0)
    assert comment_node is not None

    documentation = extract_predicate_documentation(comment_node)

    assert documentation.signature == "some_predicate/2"
    assert documentation.description == "This is some predicate description."
    assert len(documentation.arguments) == 2
    assert documentation.arguments[0].identifier == "X"
    assert documentation.arguments[0].description == "first argument"
    assert documentation.arguments[1].identifier == "Y"
    assert documentation.arguments[1].description == "second argument"


def test_extract_predicate_documentation_missing_description(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting PredicateDocumentation when description is missing."""

    source = """
    %*! some_predicate(X,Y)
    Args:
        - X:
        - Y: second argument
    *%"""
    tree = parse_to_tree(source)
    comment_node = tree.root_node.child(0)
    assert comment_node is not None

    documentation = extract_predicate_documentation(comment_node)

    assert documentation.signature == "some_predicate/2"
    assert documentation.description == ""
    assert len(documentation.arguments) == 2
    assert documentation.arguments[0].identifier == "X"
    assert documentation.arguments[0].description == ""
    assert documentation.arguments[1].identifier == "Y"
    assert documentation.arguments[1].description == "second argument"


def test_extract_predicate_documentation_missing_argument_description(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting PredicateDocumentation when an argument description is missing."""

    source = """
    %*! some_predicate(X,Y)
    This is some predicate description.
    Args:
       - X:
       - Y: second argument
    *%"""
    tree = parse_to_tree(source)
    comment_node = tree.root_node.child(0)
    assert comment_node is not None

    documentation = extract_predicate_documentation(comment_node)

    assert documentation.signature == "some_predicate/2"
    assert documentation.description == "This is some predicate description."
    assert len(documentation.arguments) == 2
    assert documentation.arguments[0].identifier == "X"
    assert documentation.arguments[0].description == ""
    assert documentation.arguments[1].identifier == "Y"
    assert documentation.arguments[1].description == "second argument"


def test_extract_predicate_documentation_only_signature(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting PredicateDocumentation when only the signature is provided."""

    source = """
    %*! some_predicate(X,Y)
    *%"""
    tree = parse_to_tree(source)
    comment_node = tree.root_node.child(0)
    assert comment_node is not None

    documentation = extract_predicate_documentation(comment_node)

    assert documentation.signature == "some_predicate/2"
    assert documentation.description == ""
    assert len(documentation.arguments) == 2
    assert all(arg.description == "" for arg in documentation.arguments)


def test_extract_predicate_documentation_no_arguments(parse_to_tree: Callable[[str], Tree]) -> None:
    """Test extracting PredicateDocumentation when there are no arguments."""

    source = """
    %*! some_predicate()
    *%"""
    tree = parse_to_tree(source)
    comment_node = tree.root_node.child(0)
    assert comment_node is not None

    documentation = extract_predicate_documentation(comment_node)

    assert documentation.signature == "some_predicate/0"
    assert documentation.description == ""
    assert len(documentation.arguments) == 0
