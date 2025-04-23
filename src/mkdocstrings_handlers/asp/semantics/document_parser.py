""" This module contains the DocumentParser class, which is responsible for parsing ASP documents.

    It extracts relevant information from the Tree-sitter parse tree and populates the Document object with
    statements, predicates, comments, and other elements.
"""

from tree_sitter import Node, Tree

from mkdocstrings_handlers.asp.document import Document
from mkdocstrings_handlers.asp.semantics.block_comment import BlockComment
from mkdocstrings_handlers.asp.semantics.directives.include import Include
from mkdocstrings_handlers.asp.semantics.directives.show import Show
from mkdocstrings_handlers.asp.semantics.line_comment import LineComment
from mkdocstrings_handlers.asp.semantics.predicate import Predicate
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
        self.current_predicates: dict[str, Predicate] = {}
        self.error = False

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

                case NodeKind.SYMBOLIC_ATOM:
                    predicate = Predicate.from_node(node.parent)
                    signature = predicate.signature

                    if signature not in self.current_predicates:
                        self.current_predicates[signature] = predicate
                    else:
                        predicate = self.current_predicates[signature]

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
                    signature = predicate.signature

                    if signature not in document.predicates:
                        document.predicates[signature] = predicate
                    else:
                        predicate = document.predicates[signature]

                    predicate.documentation = predicate_documentation
                    predicate.documentation.node = None
                case NodeKind.SHOW_SIGNATURE | NodeKind.SHOW | NodeKind.SHOW_TERM:
                    show = Show.from_node(node)
                    if show:
                        predicate = show.predicate
                        if predicate.signature in self.current_predicates:
                            predicate = self.current_predicates[predicate.signature]
                        else:
                            self.current_predicates[predicate.signature] = predicate

                        predicate.update_show_status(show.predicate.show_status)

                        # If the show directive is not empty
                        # default show behaviour depends on the show directive
                        document.disable_default_show |= show.disable_default

                        # We regard the found predicate as a provided predicate
                        # in order to track its dependencies
                        self.current_statement.add_provided(predicate)
                    else:
                        # If show returns None
                        # this means that the show directive was empty
                        # and we should disable the default show behaviour
                        document.disable_default_show = True

                case NodeKind.INCLUDE:
                    include = Include.from_node(document.path, node)
                    document.includes.append(include)
                case NodeKind.ERROR:
                    self.error = True
                case _:
                    pass

        def _on_exit(node: Node) -> None:
            """
            Handle exiting a node.

            Args:
                node: The node.
            """
            match NodeKind.from_grammar_name(node.grammar_name):
                case NodeKind.STATEMENT:
                    if self.error:
                        self._reset()
                        return

                    # The statement is done
                    document.statements.append(self.current_statement)
                    document.ordered_objects.append(self.current_statement)

                    for signature, predicate in self.current_predicates.items():
                        if signature not in document.predicates:
                            document.predicates[signature] = predicate
                        else:
                            document.predicates[signature].update_show_status(predicate.show_status)

                    self._reset()

                case NodeKind.LITERAL_TUPLE:
                    self.inside_tuple = False
                case _:
                    pass

        self._reset()
        traverse(tree, _on_enter, _on_exit)

        return document
