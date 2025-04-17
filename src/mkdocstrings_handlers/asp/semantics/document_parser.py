""" This module contains the DocumentParser class, which is responsible for parsing ASP documents.

    It extracts relevant information from the Tree-sitter parse tree and populates the Document object with
    statements, predicates, comments, and other elements.
"""

from tree_sitter import Node, Tree

from mkdocstrings_handlers.asp.document import Document
from mkdocstrings_handlers.asp.semantics.block_comment import BlockComment
from mkdocstrings_handlers.asp.semantics.directives.include import Include
from mkdocstrings_handlers.asp.semantics.directives.show_signature import ShowSignature
from mkdocstrings_handlers.asp.semantics.line_comment import LineComment
from mkdocstrings_handlers.asp.semantics.predicate import Predicate, ShowStatus
from mkdocstrings_handlers.asp.semantics.predicate_documentation import PredicateDocumentation
from mkdocstrings_handlers.asp.semantics.statement import Statement
from mkdocstrings_handlers.asp.tree_sitter.node_kind import NodeKind
from mkdocstrings_handlers.asp.tree_sitter.traverse import traverse


class DocumentParser:
    """
    A parser for ASP documents.
    """

    def __init__(self):
        """
        Initialize the parser.
        """
        self._reset()

    def _reset(self) -> None:
        """
        Reset the parser state.
        """
        self.head = True
        self.inside_tuple = False
        self.current_statement: Statement | None = None

    def parse(self, document: Document, tree: Tree) -> Document:
        """
        Parse the given tree.

        Args:
            tree: The tree to parse.
        """

        def _on_enter(node: Node) -> None:
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
                    self.current_statement = Statement.from_node(node)
                    document.statements.append(self.current_statement)
                    document.ordered_objects.append(self.current_statement)

                case NodeKind.SYMBOLIC_ATOM:
                    predicate = Predicate.from_node(node.parent)
                    signature = str(predicate)

                    if signature not in document.predicates:
                        document.predicates[signature] = predicate
                    else:
                        predicate = document.predicates[signature]

                    if self.head and not self.inside_tuple:
                        self.current_statement.add_provided(predicate)
                    else:
                        self.current_statement.add_needed(predicate)

                case NodeKind.LINE_COMMENT:
                    line_comment = LineComment.from_node(node)
                    document.line_comments.append(line_comment)
                    document.ordered_objects.append(line_comment)
                case NodeKind.BLOCK_COMMENT:
                    block_comment = BlockComment.from_node(node)
                    document.block_comments.append(block_comment)

                    # Predicate documentation
                    predicate_documentation = PredicateDocumentation.from_block_comment(block_comment)
                    if predicate_documentation is None:
                        document.ordered_objects.append(block_comment)
                        return

                    predicate = Predicate.from_node(predicate_documentation.node)
                    signature = str(predicate)

                    if signature not in document.predicates:
                        document.predicates[signature] = predicate
                    else:
                        predicate = document.predicates[signature]

                    predicate.documentation = predicate_documentation
                    predicate.documentation.node = None

                case NodeKind.SHOW_SIGNATURE:
                    sig = ShowSignature.from_node(node)

                    if sig.signature in document.predicates:
                        document.predicates[sig.signature].update_show_status(ShowStatus.EXPLICIT)

                case NodeKind.INCLUDE:
                    include = Include.from_node(document.path, node)
                    document.includes.append(include)
                case _:
                    pass

        def _on_exit(node: Node) -> None:
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

        self._reset()
        traverse(tree, _on_enter, _on_exit)

        return document
