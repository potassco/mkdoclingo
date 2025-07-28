"""This module contains the 'PredicateDocumentation', which represents the documentation for a predicate."""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field

from tree_sitter import Node

from mkdocstrings_handlers.asp.semantics.block_comment import BlockComment
from mkdocstrings_handlers.asp.tree_sitter.node_kind import NodeKind
from mkdocstrings_handlers.asp.tree_sitter.parser import ASPParser
from mkdocstrings_handlers.asp.tree_sitter.traverse import traverse


@dataclass
class PredicateParameterDocumentation:
    """
    Documentation for a parameter of a predicate.
    """

    name: str
    """ The name of the parameter. """
    type: str | None = None
    """ The type of the parameter. """
    description: str = ""
    """ The description of the parameter. """

    def __str__(self) -> str:
        return f"{self.name} ({self.type}) : {self.description}"


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
    parameter_documentations: dict[str, PredicateParameterDocumentation] = field(default_factory=dict)
    """ The documentation of the parameters of the predicate. """
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

        signature_re = r"(?P<signature>.*?)\n\s*\.{5,}\n"
        description_re = r"(?P<description>.*?)Args:"
        args_re = r"(?P<args>.*?(?=\n\S|\Z))"

        docstring_re = re.compile(
            signature_re + description_re + args_re,
            re.DOTALL | re.MULTILINE,
        )

        match = docstring_re.match(comment.text)

        if not match:
            return None

        # Get the signature
        signature = match.group("signature").strip()

        # Parse the signature to get the literal
        predicate_node = None

        def identifier_from_node(node: Node):
            nonlocal predicate_node
            if NodeKind.from_grammar_name(node.grammar_name) == NodeKind.SYMBOLIC_ATOM:
                predicate_node = node.parent

        parser = ASPParser()
        tree = parser.parse(f"{signature}.")
        traverse(tree, identifier_from_node, lambda _: None)

        description = textwrap.dedent(match.group("description")).strip()
        args = textwrap.dedent(match.group("args"))

        args_name = r"(?P<name>\w+)"
        args_type = r"(?:\s*\((?P<type>[^)]+)\))?"
        args_description = r"\s*:\s*(?P<description>.+?)"

        args_re = rf"^{args_name}{args_type}\s*{args_description}(?=(?:^\S|\Z))"

        args_matches = re.finditer(args_re, args, re.MULTILINE | re.DOTALL)

        parameter_documentations: dict[str, PredicateParameterDocumentation] = {}

        for args_match in args_matches:
            arg_name = args_match.group("name").strip()
            arg_type = args_match.group("type").strip() if args_match.group("type") else ""
            arg_description = args_match.group("description").strip()

            parameter_documentations[arg_name] = PredicateParameterDocumentation(
                name=arg_name,
                type=arg_type,
                description=arg_description,
            )

        return PredicateDocumentation(
            signature=signature,
            description=description,
            parameter_documentations=parameter_documentations,
            node=predicate_node,
        )
