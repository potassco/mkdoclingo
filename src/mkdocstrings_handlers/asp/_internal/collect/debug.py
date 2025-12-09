"""Utility functions for debugging tree-sitter trees."""

from tree_sitter import Node


def print_tree(node: Node, source: bytes, depth: int) -> None:
    """Recursively print the tree structure of a node.
    Args:
        node: The node to print.
        source: The source code from which the node was created.
        depth: The current depth in the tree.
    """
    if node.text is None:
        raise ValueError(f"Text of node {node} is None.")

    node_text = node.text.decode("utf-8")

    print(f"{'  ' * depth}{node.grammar_name} {node.id}: {node_text}")

    for child in node.children:
        print_tree(child, source, depth + 1)
