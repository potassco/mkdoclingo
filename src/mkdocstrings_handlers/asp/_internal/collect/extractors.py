"""Extractors for various ASP constructs from Tree-sitter nodes."""

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
from mkdocstrings_handlers.asp._internal.error import ExtractionError


def get_node_text(node: Node | None) -> str:
    """
    Safely extracts and decodes text from a Tree-sitter node.

    Args:
        node: The Tree-sitter node.

    Returns:
        The decoded text content of the node.

    Raises:
        ExtractionError: If the node is None or has no text.
    """
    if node is None:
        raise ExtractionError("Expected a node, but got None.")

    if node.text is None:
        # This usually happens with 'missing' nodes in Tree-sitter (syntax errors)
        raise ExtractionError(f"Node {node.type} exists but has no text content.")

    return node.text.decode("utf-8")


def get_capture_text(captures: dict[str, list[Node]], key: str, index: int = 0) -> str:
    """
    Safely retrieves the text from a capture group.

    Args:
        captures: The dictionary of captured nodes.
        key: The capture group name (e.g., "identifier").
        index: Which item in the capture list to retrieve (default 0).

    Returns:
        The decoded text content of the specified capture.

    Raises:
        ExtractionError: If the capture group is missing, empty, or the index is out of
        bounds.
    """
    nodes = captures.get(key)

    if not nodes:
        raise ExtractionError(f"Required capture group '{key}' is missing or empty.")

    if index >= len(nodes):
        raise ExtractionError(f"Capture group '{key}' does not have an element at index {index}.")

    return get_node_text(nodes[index])


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
    file_path = Path(get_node_text(file_path_node.children[1]))

    return Include((parent_file_path.parent / file_path))


def extract_predicate(node: Node) -> Predicate:
    """
    Extract a Predicate from a node.

    Args:
        node: A `literal` node representing the predicate.

    Returns:
        The created Predicate.
    """
    captures = Queries.PREDICATE.captures(node)

    return Predicate(
        identifier=get_node_text(captures["identifier"][0]),
        arity=len(captures.get("term", [])),
        negation=len(captures.get("negation", [])) > 0,
    )


def extract_show(node: Node) -> Show:
    """
    Extract a Show directive from a node.

    Args:
        node: A `show_signature` or `show_term` node representing the show directive.

    Returns:
        The created Show directive.
    """
    captures = Queries.SHOW.captures(node)

    raw_identifier = captures.get("identifier", [])
    raw_arity = captures.get("arity", [])
    raw_terms = captures.get("term", [])

    identifier: str | None = get_node_text(raw_identifier[0]) if raw_identifier else None
    arity: int | None = int(get_node_text(raw_arity[0])) if raw_arity else None
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
    """
    Extract a LineComment from a node.

    Args:
        node: A `line_comment` node representing the line comment.

    Returns:
        The created LineComment.
    """
    return LineComment(
        row=node.start_point.row,
        content=get_node_text(node).removeprefix("%"),
    )


def extract_block_comment(node: Node) -> BlockComment:
    """
    Extract a BlockComment from a node.

    Args:
        node: A `block_comment` node representing the block comment.

    Returns:
        The created BlockComment.
    """
    return BlockComment(
        row=node.start_point.row,
        content=get_node_text(node).removeprefix("%*").removesuffix("*%"),
    )


def extract_statement(node: Node) -> Statement:
    """
    Extract a Statement from a node.

    Args:
        node: A node representing the statement.

    Returns:
        The created Statement.
    """
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
        content=get_node_text(node),
        provided_predicates=provided_predicates,
        needed_predicates=needed_predicates,
    )


def extract_argument_documentation(node: Node) -> ArgumentDocumentation:
    """
    Extract an ArgumentDocumentation from a node.

    Args:
        node: The node representing the argument documentation.

    Returns:
        The created ArgumentDocumentation.
    """
    captures = Queries.DOC_ARGUMENT.captures(node)

    identifier = get_capture_text(captures, "identifier", 0)
    description = get_node_text(captures["description"][0]).strip() if captures.get("description") else ""

    return ArgumentDocumentation(
        identifier=identifier,
        description=description,
    )


def extract_predicate_documentation(node: Node) -> PredicateDocumentation:
    """
    Extract a PredicateDocumentation from a node.

    Args:
        node: The node representing the predicate documentation.

    Returns:
        The created PredicateDocumentation.
    """
    captures = Queries.DOC_PREDICATE.captures(node)

    identifier = get_capture_text(captures, "identifier", 0)

    # For some reason the query does not return the arguments
    # in the order they appear. So we order them by their start byte.
    argument_nodes = captures.get("argument", [])
    argument_nodes.sort(key=lambda n: n.start_byte)
    arguments = [get_node_text(arg) for arg in argument_nodes]

    explicit_docs_map = {}
    for arg_node in captures.get("arg.documentation", []):
        doc = extract_argument_documentation(arg_node)
        explicit_docs_map[doc.identifier] = doc

    final_arguments = []
    for name in arguments:
        if name in explicit_docs_map:
            final_arguments.append(explicit_docs_map[name])
        else:
            final_arguments.append(ArgumentDocumentation(identifier=name, description=""))

    description = (
        get_node_text(captures["description"][0]).removeprefix("%*!").removesuffix("*%").strip()
        if captures.get("description")
        else ""
    )

    return PredicateDocumentation(
        row=node.start_point.row,
        content=get_node_text(node),
        signature=f"{identifier}/{len(arguments)}",
        description=description,
        arguments=final_arguments,
    )
