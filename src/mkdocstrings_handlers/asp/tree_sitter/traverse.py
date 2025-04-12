""" This module contains the function to traverse a tree-sitter tree in a pre-order depth-first manner. """

from typing import Callable

from tree_sitter import Node, Tree


def traverse(tree: Tree, on_enter: Callable[[Node], None], on_exit: Callable[[Node], None]) -> None:
    """
    Traverse the given tree in pre-order depth-first manner and call the given functions on each node.

    Args:
        tree: The tree to traverse.
        on_enter: The function to call when entering a node.
        on_exit: The function to call when exiting a node.

    Returns:
        None
    """
    cursor = tree.walk()

    while True:
        # Visit node the first time
        on_enter(cursor.node)

        # Travel down as far as possible
        if cursor.goto_first_child():
            continue

        # If the lowest node is reached, traverse to sibling
        if cursor.goto_next_sibling():
            continue

        # If neither is possible, traverse back up
        while True:
            # Stop traversing if root node is reached
            if not cursor.goto_parent():
                return

            on_exit(cursor.node)

            # Since we've already visited the parent on the way down,
            # try to traverse to sibling and start to move down again
            if cursor.goto_next_sibling():
                break
