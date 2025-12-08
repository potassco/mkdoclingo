from pathlib import Path

from mkdocstrings_handlers.asp._internal.collect.load import load_documents
from mkdocstrings_handlers.asp._internal.domain import ShowStatus
from mkdocstrings_handlers.asp._internal.render import get_render_context


def test_get_render_context_no_show(tmp_path: Path):
    file_path = tmp_path / "base_file.lp"
    file_content = ("p(a, b).\n"
                    "p(1,2).\n"
                    )
    file_path.write_bytes(file_content.encode("utf-8"))
    documents = load_documents([file_path])
    context = get_render_context(documents)

    assert len(context.predicates) == 1
    assert all(predicate.show_status == ShowStatus.DEFAULT for predicate in context.predicates)

def test_get_render_context_show_empty(tmp_path: Path):
    file_path = tmp_path / "base_file.lp"
    file_content = ("a(1,2,3).\n"
                    "p(1,2).\n"
                    "#show ."
                    )
    file_path.write_bytes(file_content.encode("utf-8"))
    documents = load_documents([file_path])
    context = get_render_context(documents)

    assert len(context.predicates) == 2
    assert all(predicate.show_status == ShowStatus.HIDDEN for predicate in context.predicates)

def test_get_render_context_show_explicit(tmp_path: Path):
    file_path = tmp_path / "base_file.lp"
    file_content = ("a(1,2,3).\n"
                    "p(1,2).\n"
                    "#show p/2."
                    )
    file_path.write_bytes(file_content.encode("utf-8"))
    documents = load_documents([file_path])
    context = get_render_context(documents)

    assert len(context.predicates) == 2
    assert context.predicates[0].signature == "a/3"
    assert context.predicates[0].show_status == ShowStatus.HIDDEN
    assert context.predicates[1].signature == "p/2"
    assert context.predicates[1].show_status == ShowStatus.EXPLICIT

def test_get_render_context_show_partial(tmp_path: Path):
    file_path = tmp_path / "base_file.lp"
    file_content = ("a(1,2,3).\n"
                    "p(1,2).\n"
                    "#show p(2,3)."
                    )
    file_path.write_bytes(file_content.encode("utf-8"))
    documents = load_documents([file_path])
    context = get_render_context(documents)

    assert len(context.predicates) == 2
    assert context.predicates[0].signature == "a/3"
    assert context.predicates[0].show_status == ShowStatus.DEFAULT
    assert context.predicates[1].signature == "p/2"
    assert context.predicates[1].show_status == ShowStatus.PARTIAL

def test_get_render_context_dependencies(tmp_path: Path):
    file_path = tmp_path / "base_file.lp"
    file_content = ("q(1..5).\n"
                    "r(3).\n"
                    "p(X):-q(X), not r(X).\n"
                    )
    file_path.write_bytes(file_content.encode("utf-8"))
    documents = load_documents([file_path])
    context = get_render_context(documents)

    assert len(context.predicates) == 3
    assert context.predicates[0].signature == "q/1"
    assert context.predicates[0].positive_dependencies == set()
    assert context.predicates[0].negative_dependencies == set()
    assert context.predicates[1].signature == "r/1"
    assert context.predicates[1].positive_dependencies == set()
    assert context.predicates[1].negative_dependencies == set()
    assert context.predicates[2].signature == "p/1"
    assert context.predicates[2].positive_dependencies == {"q/1"}
    assert context.predicates[2].negative_dependencies == {"r/1"}