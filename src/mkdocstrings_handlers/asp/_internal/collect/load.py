import logging
from collections import deque
from pathlib import Path

from mkdocstrings_handlers.asp._internal.collect.extractors import (
    extract_block_comment,
    extract_include,
    extract_line_comment,
    extract_statement,
)
from mkdocstrings_handlers.asp._internal.collect.syntax import NodeKind, get_parser
from mkdocstrings_handlers.asp._internal.domain import Document

log = logging.getLogger(__name__)

def load_documents(paths: list[Path]) -> list[Document]:
    parse_queue = deque(paths)
    documents: dict[Path, Document] = {}
    while parse_queue:
        path = parse_queue.popleft()
        if path.suffix != ".lp" or not path.is_file():
            log.warning(f"skip file {path}, not a valid ASP file.")
            continue
        document = load_document(path)
        documents[path] = document
        parse_queue.extend(include.path for include in document.includes if include.path not in documents)

    return list(documents.values())

def load_document(file_path: Path) -> Document:
    with open(file_path, "rb") as f:
        source_bytes = f.read()

    document = Document(path=file_path, content=source_bytes.decode("utf-8"))
    tree = get_parser().parse(source_bytes)

    for node in tree.root_node.children:
        match NodeKind.from_grammar_name(node.grammar_name):
            case NodeKind.RULE:
                statement = extract_statement(node)
                document.statements.append(statement)
            case NodeKind.LINE_COMMENT:
                comment = extract_line_comment(node)
                document.line_comments.append(comment)
            case NodeKind.BLOCK_COMMENT:
                comment = extract_block_comment(node)
                document.block_comments.append(comment)
            case NodeKind.INCLUDE:
                include = extract_include(node, file_path)
                document.includes.append(include)

    return document
