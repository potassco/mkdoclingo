"""Utility functions for debugging tree-sitter trees."""

from tree_sitter import Node


def print_tree(node: Node, source: bytes, depth: int) -> None:
    node_text = node.text.decode("utf-8")
    print(f"{'  ' * depth}{node.grammar_name} {node.id}: {node_text}")

    for i in range(node.child_count):
        child = node.child(i)
        print_tree(child, source, depth + 1)
