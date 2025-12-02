import logging
from collections import deque
from pathlib import Path

import tree_sitter_clingo
from tree_sitter import Language, Parser

from mkdocstrings_handlers.asp._internal.document import Document
from mkdocstrings_handlers.asp._internal.semantics.directives.include import Include
from mkdocstrings_handlers.asp._internal.tree_sitter.debug import print_tree
from mkdocstrings_handlers.asp._internal.tree_sitter.node_kind import NodeKind

log = logging.getLogger(__name__)


class ASPParser:
    def __init__(self):
        language = Language(tree_sitter_clingo.language())
        self._parser = Parser(language)

    def parse_files(self, paths: list[Path]) -> list[Document]:
        parse_queue = deque(paths)
        documents: dict[Path, Document] = {}
        while parse_queue:
            path = parse_queue.popleft()
            if path.suffix != ".lp" or not path.is_file():
                log.warning(f"skip file {path}, not a valid ASP file.")
                continue
            document = self.parse_file(path)
            documents[path] = document
            parse_queue.extend(include.path for include in document.includes if include.path not in documents)

        return documents.values()

    def parse_file(self, file_path: Path) -> Document:
        with open(file_path, "rb") as f:
            source_bytes = f.read()

        document = Document(path=file_path, content=source_bytes.decode("utf-8"))
        tree = self._parser.parse(source_bytes)

        # print_tree(tree.root_node, source_bytes, depth=1)

        for node in tree.root_node.children:
            match NodeKind.from_grammar_name(node.grammar_name):
                case NodeKind.RULE:
                    pass
                case NodeKind.INCLUDE:
                    include = Include.from_node(node)
                    include.resolve_path(file_path)
                    document.includes.append(include)

        return document
