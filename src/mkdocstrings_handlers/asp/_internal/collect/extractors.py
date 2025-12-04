from pathlib import Path

from tree_sitter import Node

from mkdocstrings_handlers.asp._internal.collect.syntax import Queries
from mkdocstrings_handlers.asp._internal.domain import BlockComment, Include, LineComment, Predicate, Statement


def extract_include(node: Node, parent_file_path: Path) -> Include:
    """
    Extract an Include from a node.

    Args:
        node: The node representing the include.
        base_path: The base path of the current file.

    Returns:
        The created Include.
    """
    # If the node is an include,
    # then the first child is the include directive
    # and the second child is the file path.

    # The second child of the file path is the file path
    # as a string fragment without the quotes.
    file_path_node = node.children[1]
    file_path = Path(file_path_node.children[1].text.decode("utf-8"))

    return Include((parent_file_path.parent / file_path).resolve())


def extract_predicate(node: Node) -> Predicate:
    captures = Queries.PREDICATE.captures(node)

    return Predicate(
        identifier=captures["identifier"][0].text.decode("utf-8"),
        arity=len(captures.get("term", [])),
        negation=len(captures.get("negation", [])) > 0,
    )


def extract_line_comment(node: Node) -> LineComment:
    return LineComment(
        row=node.start_point.row,
        content=node.text.decode("utf-8").removeprefix("%"),
    )


def extract_block_comment(node: Node) -> BlockComment:
    return BlockComment(
        row=node.start_point.row,
        content=node.text.decode("utf-8").removeprefix("%*").removesuffix("*%"),
    )


def extract_statement(node: Node) -> Statement:
    head_node = node.child_by_field_name("head")
    body_node = node.child_by_field_name("body")

    captures = {}

    if head_node:
        # We don't use the head_node here
        # because `head` is a supertype in the current grammar
        # which leads to query difficulties with literals
        head_captures = Queries.HEAD.captures(node)
        captures.update(head_captures)

    if body_node:
        body_captures = Queries.BODY.captures(body_node)
        captures.update(body_captures)

    provided_predicates = [extract_predicate(node) for node in captures.get("provided", [])]
    needed_predicates = [extract_predicate(node) for node in captures.get("needed", [])]

    return Statement(
        row=node.start_point.row,
        text=node.text.decode("utf-8"),
        provided_predicates=provided_predicates,
        needed_predicates=needed_predicates,
    )
