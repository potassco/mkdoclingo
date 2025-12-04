from pathlib import Path

from mkdocstrings_handlers.asp._internal.collect.collectors import collect_from_file, collect_from_files


def test_collect_from_file(tmp_path: Path) -> None:
    """Test collecting a Document from a file."""

    file_path = tmp_path / "base_file.lp"
    file_content = "q(X) :- p(X, Y)."
    file_path.write_bytes(file_content.encode("utf-8"))

    document = collect_from_file(file_path)
    
    assert document.path == file_path
    assert document.content == file_content
    assert len(document.includes) == 0
    assert len(document.statements) == 1
    assert len(document.ordered_elements) == 1

def test_collect_from_file_empty(tmp_path: Path) -> None:
    """Test collecting a Document from an empty file."""

    file_path = tmp_path / "empty_file.lp"
    file_content = ""
    file_path.write_bytes(file_content.encode("utf-8"))

    document = collect_from_file(file_path)
    
    assert document.path == file_path
    assert document.content == file_content
    assert len(document.includes) == 0
    assert len(document.statements) == 0
    assert len(document.ordered_elements) == 0

def test_collect_from_files(tmp_path: Path) -> None:
    """
    Test collecting a Document from a file containing an import.
    
    The imported file should also be collected.
    """

    file_path = tmp_path / "base_file.lp"
    file_content = ("#include \"includes/included_file.lp\".\n"
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

    documents = collect_from_files([file_path])
    assert len(documents) == 2

    document = next(doc for doc in documents if doc.path == file_path)
    assert document.path == file_path
    assert document.content == file_content
    assert len(document.includes) == 1
    assert len(document.statements) == 2
    assert len(document.ordered_elements) == 5
    assert document.includes[0].path == included_file_path

    included_document = next(doc for doc in documents if doc.path == included_file_path)
    assert included_document.content == included_file_content
    assert len(included_document.statements) == 1
    assert len(included_document.ordered_elements) == 1
    assert included_document.content == included_file_content

def test_collect_from_files_invalid_include(tmp_path: Path) -> None:
    """
    Test collecting a Document from a file containing an invalid import.
    
    The invalid include should be skipped.
    """

    file_path = tmp_path / "base_file.lp"
    file_content = ("#include \"includes/missing\".\n"
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

    documents = collect_from_files([file_path])
    assert len(documents) == 1

    document = documents[0]
    assert document.path == file_path
    assert document.content == file_content
    assert len(document.includes) == 1
    assert len(document.statements) == 2
    assert len(document.ordered_elements) == 5