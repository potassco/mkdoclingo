from __future__ import annotations

from dataclasses import dataclass

from tree_sitter import Node


@dataclass
class Literal:
    identifier: str
    arity: int
    negation: bool

    @staticmethod
    def from_node(node: Node) -> Literal:
        # If the literal has a single child, it is positive

        negation = node.child_count > 1 and node.children[0].child_count == 1

        atom = node.children[0] if node.child_count == 1 else node.children[1]

        identifier = atom.children[0].text.decode("utf-8")

        if atom.child_count == 1:
            arity = 0
        else:
            terms = atom.children[1].children[0]
            arity = len(terms.children) // 2

        return Literal(identifier, arity, negation)
