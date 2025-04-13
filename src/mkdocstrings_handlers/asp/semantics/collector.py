""" This module contains the Collector class, which is used to collect data from an ASP document.

The Collector class traverses the tree of the document and collects information about various elements,
including statements, comments and predicates.
"""

from tree_sitter import Node

from mkdocstrings_handlers.asp.semantics.block_comment import BlockComment
from mkdocstrings_handlers.asp.semantics.directives.include import Include
from mkdocstrings_handlers.asp.semantics.directives.show_signature import ShowSignature
from mkdocstrings_handlers.asp.semantics.line_comment import LineComment
from mkdocstrings_handlers.asp.semantics.predicate import Predicate
from mkdocstrings_handlers.asp.semantics.predicate_documentation import PredicateDocumentation
from mkdocstrings_handlers.asp.tree_sitter.node_kind import NodeKind
from mkdocstrings_handlers.asp.tree_sitter.traverse import traverse

from .statement import Statement


class Collector:
    """
    A collector for data in an ASP document.
    """

    def __init__(self):
        """
        Initialize the collector.
        """

        # state management
        self.head = True
        self.inside_tuple = False

        # data
        self.statements: list[Statement] = []
        self.line_comments: list[LineComment] = []
        self.block_comments: list[BlockComment] = []
        self.predicates: dict[str, Predicate] = {}
        self.includes: list[Include] = []

    def collect(self, tree):
        """
        Collect data from the given tree.
        """

        traverse(tree, self._on_enter, self._on_exit)

    def _on_enter(self, node: Node):
        """
        Handle entering a node.

        Args:
            node: The node.
        """

        match NodeKind.from_grammar_name(node.grammar_name):
            # State management
            case NodeKind.HEAD:
                self.head = True
            case NodeKind.BODY:
                self.head = False
            case NodeKind.LITERAL_TUPLE:
                self.inside_tuple = True

            # Data collection
            case NodeKind.STATEMENT:
                statement = Statement.from_node(node)
                self.statements.append(statement)
            case NodeKind.SYMBOLIC_ATOM:
                predicate = Predicate.from_node(node.parent)
                statement = self.statements[-1]

                if str(predicate) not in self.predicates:
                    self.predicates[str(predicate)] = predicate
                else:
                    predicate = self.predicates[str(predicate)]

                if self.head and not self.inside_tuple:
                    statement.add_provided(predicate)
                else:
                    statement.add_needed(predicate)
            case NodeKind.LINE_COMMENT:
                line_comment = LineComment.from_node(node)
                self.line_comments.append(line_comment)
            case NodeKind.BLOCK_COMMENT:
                block_comment = BlockComment.from_node(node)
                self.block_comments.append(block_comment)

                # Predicate documentation
                predicate_documentation = PredicateDocumentation.from_block_comment(block_comment)
                if predicate_documentation is None:
                    return

                predicate = Predicate.from_node(predicate_documentation.node)

                if str(predicate) not in self.predicates:
                    self.predicates[str(predicate)] = predicate
                else:
                    predicate = self.predicates[str(predicate)]

                predicate.documentation = predicate_documentation
                predicate.documentation.node = None

            case NodeKind.SHOW_SIGNATURE:
                ShowSignature.from_node(node)

            case NodeKind.INCLUDE:
                include = Include.from_node(node)
                self.includes.append(include)
            case _:
                pass

    def _on_exit(self, node: Node):
        """
        Handle exiting a node.

        Args:
            node: The node.
        """
        match NodeKind.from_grammar_name(node.grammar_name):
            case NodeKind.LITERAL_TUPLE:
                self.inside_tuple = False
            case _:
                pass
