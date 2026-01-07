"""This module contains tests for loading ASP documents."""

from pathlib import Path

from mkdocstrings_handlers.asp._internal.collect.load import load_document, load_documents
from mkdocstrings_handlers.asp._internal.domain import ShowStatus


def test_load_from_file(tmp_path: Path) -> None:
    """Test loading a Document from a file."""

    file_path = tmp_path / "base_file.lp"
    file_content = (
        "%*! q(X)\n"
        "This is a description of q.\n"
        "Args:\n"
        "   - X: This is a description of X\n"
        "*%\n"
        "q(X) :- p(X, Y).\n"
        "#show q/1.\n"
        "#show p(1,2)."
    )
    file_path.write_bytes(file_content.encode("utf-8"))

    document = load_document(file_path)

    assert document.path == file_path
    assert document.content == file_content
    assert len(document.includes) == 0
    assert len(document.statements) == 3
    assert len(document.line_comments) == 0
    assert len(document.block_comments) == 0
    assert len(document.predicate_documentations) == 1
    assert len(document.shows) == 2
    assert document.shows[0].status == ShowStatus.EXPLICIT
    assert document.shows[1].status == ShowStatus.PARTIAL


def test_load_from_file_empty(tmp_path: Path) -> None:
    """Test loading a Document from an empty file."""

    file_path = tmp_path / "empty_file.lp"
    file_content = ""
    file_path.write_bytes(file_content.encode("utf-8"))

    document = load_document(file_path)

    assert document.path == file_path
    assert document.content == file_content
    assert len(document.includes) == 0
    assert len(document.statements) == 0
    assert len(document.line_comments) == 0
    assert len(document.block_comments) == 0
    assert len(document.predicate_documentations) == 0


def test_load_from_files(tmp_path: Path) -> None:
    """
    Test loading a Document from a file containing an import.

    The imported file should also be loaded.
    """

    file_path = tmp_path / "base_file.lp"
    file_content = (
        '#include "includes/included_file.lp".\n'
        "%* This is a\n"
        "   block comment *%\n"
        "p(a, b).\n"
        "% This is a line comment\n"
        "% p(1,2,3).\n"
        "p(1,2).\n"
    )

    file_path.write_bytes(file_content.encode("utf-8"))
    includes_path = tmp_path / "includes"
    includes_path.mkdir()
    included_file_path = includes_path / "included_file.lp"
    included_file_content = "q(X) :- p(X, Y)."
    included_file_path.write_text(included_file_content)

    documents = load_documents([file_path])
    assert len(documents) == 2

    document = next(doc for doc in documents if doc.path == file_path)
    assert document.path == file_path
    assert document.content == file_content
    assert len(document.includes) == 1
    assert len(document.statements) == 2
    assert len(document.line_comments) == 2
    assert len(document.block_comments) == 1
    assert len(document.predicate_documentations) == 0
    assert document.includes[0].path == included_file_path

    included_document = next(doc for doc in documents if doc.path == included_file_path)
    assert included_document.content == included_file_content
    assert len(included_document.statements) == 1
    assert len(included_document.line_comments) == 0
    assert len(included_document.block_comments) == 0
    assert len(document.predicate_documentations) == 0
    assert included_document.content == included_file_content


def test_load_from_files_invalid_include(tmp_path: Path) -> None:
    """
    Test loading a Document from a file containing an invalid import.

    The invalid include should be skipped.
    """

    file_path = tmp_path / "base_file.lp"
    file_content = (
        '#include "includes/missing".\n'
        "%* This is a\n"
        "   block comment *%\n"
        "p(a, b).\n"
        "% This is a line comment\n"
        "% p(1,2,3).\n"
        "p(1,2).\n"
    )

    file_path.write_bytes(file_content.encode("utf-8"))
    includes_path = tmp_path / "includes"
    includes_path.mkdir()
    included_file_path = includes_path / "included_file.lp"
    included_file_content = "q(X) :- p(X, Y)."
    included_file_path.write_text(included_file_content)

    documents = load_documents([file_path])
    assert len(documents) == 1

    document = documents[0]
    assert document.path == file_path
    assert document.content == file_content
    assert len(document.includes) == 1
    assert len(document.statements) == 2
    assert len(document.line_comments) == 2
    assert len(document.block_comments) == 1
    assert len(document.predicate_documentations) == 0
