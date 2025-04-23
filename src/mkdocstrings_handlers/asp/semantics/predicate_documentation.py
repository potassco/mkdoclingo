"""This module contains the 'PredicateDocumentation', which represents the documentation for a predicate."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field

from tree_sitter import Node

from mkdocstrings_handlers.asp.semantics.block_comment import BlockComment
from mkdocstrings_handlers.asp.tree_sitter.node_kind import NodeKind
from mkdocstrings_handlers.asp.tree_sitter.parser import ASPParser
from mkdocstrings_handlers.asp.tree_sitter.traverse import traverse


@dataclass
class PredicateDocumentation:
    """
    Documentation for a predicate.


    Example:
        %*#some_predicate(A,B,C).
        description
        #parameters
        - A : this is  A
        - B : this is  B
        - C : this is  C
        *%
    """

    signature: str
    """ The signature of the predicate. """
    description: str
    """ The description of the predicate. """
    parameter_descriptions: dict[str, str] = field(default_factory=dict)
    """ The descriptions of the parameters of the predicate. """
    node: Node | None = None
    """ The node representing the predicate. """

    @staticmethod
    def from_block_comment(comment: BlockComment) -> PredicateDocumentation | None:
        """
        Create a predicate documentation from a comment.

        Args:
            comment: The block comment.

        Returns:
            The predicate documentation or None if the comment is not a predicate documentation.
        """
        if not comment.lines[0].startswith("#"):
            return None

        # Get the signature
        signature = comment.lines[0].removeprefix("#").strip()

        # Parse the signature to get the literal
        predicate_node = None

        def identifier_from_node(node: Node):
            nonlocal predicate_node
            if NodeKind.from_grammar_name(node.grammar_name) == NodeKind.SYMBOLIC_ATOM:
                predicate_node = node.parent

        parser = ASPParser()
        tree = parser.parse(signature)
        traverse(tree, identifier_from_node, lambda _: None)

        # Get the description
        description_lines = []

        for line in comment.lines[1:]:
            if line.startswith("#parameters"):
                description = line.removeprefix("#").strip()
                break
            description_lines.append(line)

        description = "\n".join(description_lines)
        parameters = []
        parameter_descriptions = {}
        for line in comment.lines[len(description_lines) :]:
            if line.startswith("-"):
                parts = line.removeprefix("-").split(":")
                if len(parts) == 2:
                    parameter, parameter_description = parts
                    parameters.append(parameter.strip())
                    parameter_descriptions[parameter.strip()] = parameter_description.strip()
        description = textwrap.dedent(description).strip()
        return PredicateDocumentation(
            signature=signature.removesuffix("."),
            description=description,
            parameter_descriptions=parameter_descriptions,
            node=predicate_node,
        )
