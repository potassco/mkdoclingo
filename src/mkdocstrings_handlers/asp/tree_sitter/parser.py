""" This module contains the ASPParser class, which uses tree-sitter to parse ASP text."""

import ctypes
import os
from sys import platform

from tree_sitter import Language, Parser, Tree


class ASPParser:
    """
    A tree-sitter parser for ASP text.
    """

    def __init__(self) -> None:
        """
        Create a new ASP parser.
        """
        # Determine the path to the shared library based on the operating system
        if platform == "linux":
            lib_path = os.path.join(os.path.dirname(__file__), "lib/clingo-language.so")
        elif platform == "darwin":
            lib_path = os.path.join(os.path.dirname(__file__), "lib/clingo-language.dylib")
        else:
            lib_path = os.path.join(os.path.dirname(__file__), "lib/clingo-language.dll")

        # Load the shared library
        clingo_lib = ctypes.cdll.LoadLibrary(lib_path)

        # Retrieve the 'tree_sitter_clingo' function
        tree_sitter_clingo = clingo_lib.tree_sitter_clingo
        tree_sitter_clingo.restype = ctypes.c_void_p

        # Create a Language object using the function pointer
        clingo_language = Language(tree_sitter_clingo())

        self.parser = Parser(clingo_language)

    def parse(self, text: str) -> Tree:
        """
        Parse the given text.

        Args:
            text: The text to parse.

        Returns:
            The parsed tree.
        """
        return self.parser.parse(bytes(text, "utf8"))
