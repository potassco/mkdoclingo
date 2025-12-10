"""This module handles loading and parsing ASP documents."""

import logging
from collections import deque
from pathlib import Path

from mkdocstrings_handlers.asp._internal.collect.extractors import (
    extract_block_comment,
    extract_include,
    extract_line_comment,
    extract_predicate_documentation,
    extract_show,
    extract_statement,
)
from mkdocstrings_handlers.asp._internal.collect.syntax import NodeKind, get_parser
from mkdocstrings_handlers.asp._internal.domain import Document, ShowStatus

log = logging.getLogger(__name__)


def load_documents(paths: list[Path]) -> list[Document]:
    """
    Load and parse multiple ASP documents from the given file paths.

    Args:
        paths: List of paths to ASP files.

    Returns:
        List of parsed Document objects.
    """
    parse_queue = deque(paths)
    documents: dict[Path, Document] = {}
    while parse_queue:
        path = parse_queue.popleft()
        if path.suffix != ".lp" or not path.is_file():
            log.warning("skip file %s, not a valid ASP file.", path)
            continue
        document = load_document(path)
        documents[path] = document
        parse_queue.extend(include.path for include in document.includes if include.path not in documents)

    return list(documents.values())


def load_document(file_path: Path) -> Document:
    """
    Load and parse an ASP document from the given file path.

    Args:
        file_path: Path to the ASP file.

    Returns:
        The parsed Document object.
    """
    with open(file_path, "rb") as f:
        source_bytes = f.read()

    document = Document(path=file_path, content=source_bytes.decode("utf-8"))
    tree = get_parser().parse(source_bytes)

    for node in tree.root_node.children:
        match NodeKind.from_grammar_name(node.grammar_name):
            case NodeKind.RULE | NodeKind.INTEGRITY_CONSTRAINT:
                statement = extract_statement(node)
                document.statements.append(statement)
            case NodeKind.LINE_COMMENT:
                line_comment = extract_line_comment(node)
                document.line_comments.append(line_comment)
            case NodeKind.BLOCK_COMMENT:
                block_comment = extract_block_comment(node)
                document.block_comments.append(block_comment)
            case NodeKind.INCLUDE:
                include = extract_include(node, file_path)
                document.includes.append(include)
            case NodeKind.SHOW | NodeKind.SHOW_SIGNATURE | NodeKind.SHOW_TERM:
                show = extract_show(node)
                statement = extract_statement(node)

                if show.predicate is not None and show.status == ShowStatus.PARTIAL:
                    statement.provided_predicates.append(show.predicate)

                document.shows.append(show)
                document.statements.append(statement)
            case NodeKind.DOC_COMMENT:
                predicate_documentation = extract_predicate_documentation(node)
                document.predicate_documentations.append(predicate_documentation)

    return document
