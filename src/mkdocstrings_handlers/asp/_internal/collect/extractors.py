from collections import defaultdict
from pathlib import Path

from tree_sitter import Node

from mkdocstrings_handlers.asp._internal.collect.syntax import Queries
from mkdocstrings_handlers.asp._internal.domain import (
    ArgumentDocumentation,
    BlockComment,
    Include,
    LineComment,
    Predicate,
    PredicateDocumentation,
    Show,
    ShowStatus,
    Statement,
)

from mkdocstrings_handlers.asp._internal.domain import ArgumentDocumentation, BlockComment, Include, LineComment, Predicate, PredicateDocumentation, Show, ShowStatus, Statement


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


def extract_show(node: Node) -> Show:
    captures = Queries.SHOW.captures(node)

    raw_identifier = captures.get("identifier", [])
    raw_arity = captures.get("arity", [])
    raw_terms = captures.get("term", [])

    identifier: str | None = raw_identifier[0].text.decode("utf-8") if raw_identifier else None
    arity: int | None = int(raw_arity[0].text.decode("utf-8")) if raw_arity else None
    predicate: Predicate | None = None
    status = ShowStatus.EXPLICIT

    if raw_terms:
        status = ShowStatus.PARTIAL
        arity = len(raw_terms)

    if identifier is not None and arity is not None:
        predicate = Predicate(
            identifier=identifier,
            arity=arity,
        )

    return Show(
        predicate=predicate,
        status=status,
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

    captures = defaultdict(list)

    if head_node:
        # We don't use the head_node here
        # because `head` is a supertype in the current grammar
        # which leads to query difficulties with literals
        head_captures = Queries.HEAD.captures(node)
        for key, nodes in head_captures.items():
            captures[key].extend(nodes)

    if body_node:
        body_captures = Queries.BODY.captures(body_node)
        for key, nodes in body_captures.items():
            captures[key].extend(nodes)

    provided_predicates = [extract_predicate(node) for node in captures.get("provided", [])]
    needed_predicates = [extract_predicate(node) for node in captures.get("needed", [])]

    return Statement(
        row=node.start_point.row,
        content=node.text.decode("utf-8"),
        provided_predicates=provided_predicates,
        needed_predicates=needed_predicates,
    )


def extract_argument_documentation(node: Node) -> ArgumentDocumentation:
    captures = Queries.DOC_ARGUMENT.captures(node)

    identifier = captures["identifier"][0].text.decode("utf-8")
    description = captures.get("description")[0].text.decode("utf-8").strip() if captures.get("description") else ""

    return ArgumentDocumentation(
        identifier=identifier,
        description=description,
    )


def extract_predicate_documentation(node: Node) -> PredicateDocumentation:
    captures = Queries.DOC_PREDICATE.captures(node)

    identifier = captures["identifier"][0].text.decode("utf-8")
    arguments = [arg.text.decode("utf-8") for arg in captures.get("argument", [])]
    description = (
        captures["description"][0].text.decode("utf-8").removeprefix("%*!").removesuffix("*%").strip()
        if captures.get("description")
        else ""
    )
    argument_documentations = [
        extract_argument_documentation(arg_node) for arg_node in captures.get("arg.documentation", [])
    ]

    return PredicateDocumentation(
        row=node.start_point.row,
        content=node.text.decode("utf-8"),
        signature=f"{identifier}/{len(arguments)}",
        description=description,
        arguments=argument_documentations,
    )
