import ctypes
import os

from tree_sitter import Language, Parser, Tree


class ASPParser:
    """
    A tree-sitter parser for ASP text.
    """

    def __init__(self) -> None:
        """
        Create a new ASP parser.
        """
        # Determine the path to the shared library
        lib_path = os.path.join(os.path.dirname(__file__), "clingo-language.so")

        # Load the shared library
        clingo_lib = ctypes.cdll.LoadLibrary(lib_path)

        # Retrieve the 'tree_sitter_clingo' function
        tree_sitter_clingo = clingo_lib.tree_sitter_clingo
        tree_sitter_clingo.restype = ctypes.c_void_p

        # Create a Language object using the function pointer
        CLINGO_LANGUAGE = Language(tree_sitter_clingo())

        self.parser = Parser(CLINGO_LANGUAGE)

    def parse(self, text: str) -> Tree:
        """
        Parse the given text.

        Args:
            text: The text to parse.

        Returns:
            The parsed tree.
        """
        return self.parser.parse(bytes(text, "utf8"))