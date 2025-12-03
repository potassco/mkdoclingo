from pathlib import Path

from tree_sitter import Node

from mkdocstrings_handlers.asp._internal.domain import Include


def extract_include(node: Node, base_path: Path) -> Include:
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

    return Include((base_path.parent / file_path).resolve())
