import logging
from collections import deque
from pathlib import Path

import tree_sitter_clingo
from tree_sitter import Language, Parser

from mkdocstrings_handlers.asp._internal.collect.debug import print_tree
from mkdocstrings_handlers.asp._internal.collect.extractors import extract_include
from mkdocstrings_handlers.asp._internal.collect.node_kind import NodeKind
from mkdocstrings_handlers.asp._internal.domain import Document, Include

log = logging.getLogger(__name__)


class DocumentCollector:
    def __init__(self):
        language = Language(tree_sitter_clingo.language())
        self._parser = Parser(language)

    def collect_from_files(self, paths: list[Path]) -> list[Document]:
        parse_queue = deque(paths)
        documents: dict[Path, Document] = {}
        while parse_queue:
            path = parse_queue.popleft()
            if path.suffix != ".lp" or not path.is_file():
                log.warning(f"skip file {path}, not a valid ASP file.")
                continue
            document = self.collect_from_file(path)
            documents[path] = document
            parse_queue.extend(include.path for include in document.includes if include.path not in documents)

        return documents.values()

    def collect_from_file(self, file_path: Path) -> Document:
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
                    include = extract_include(node, file_path)
                    document.includes.append(include)

        return document
