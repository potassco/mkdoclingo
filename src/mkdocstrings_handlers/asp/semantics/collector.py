from tree_sitter import Node

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

    def collect(self, tree):
        """
        Collect data from the given tree.
        """

        traverse(tree, self._on_enter, self._on_exit)
        return

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
                literal = Literal.from_node(node.parent)
                statement = self.statements[-1]

                if self.head and not self.inside_tuple:
                    statement.add_provided(literal)
                else:
                    statement.add_needed(literal)
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
