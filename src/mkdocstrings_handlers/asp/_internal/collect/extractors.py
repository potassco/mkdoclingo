from pathlib import Path

from tree_sitter import Node

from mkdocstrings_handlers.asp._internal.collect.syntax import Queries
from mkdocstrings_handlers.asp._internal.domain import Include, Predicate, Statement


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


def extract_statement(node: Node) -> Statement:
    head_node = node.child_by_field_name("head")
    body_node = node.child_by_field_name("body")

    if head_node:
        captures = Queries.HEAD.captures(head_node)

    if body_node:
        captures = Queries.BODY.captures(body_node)

    print(captures)

    return Statement(
        row=node.start_point.row, text=node.text.decode("utf-8"), provided_predicates=[], needed_predicates=[]
    )
