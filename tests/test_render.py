"""This module contains tests for the rendering context."""

from pathlib import Path

from mkdocstrings_handlers.asp._internal.collect.load import load_documents
from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.render.render_context import RenderContext


def test_dependency_graph_structure(tmp_path: Path) -> None:
    """Test that the dependency graph context is built correctly."""

    file_path = tmp_path / "graph.lp"
    file_path.write_text("p(X) :- q(X), not r(X).", encoding="utf-8")

    documents = load_documents([file_path])
    context = RenderContext(_documents=documents, options=ASPOptions())

    graph = context.dependency_graph

    assert "p/1" in graph.all
    assert "q/1" in graph.all
    assert "r/1" in graph.all
    assert ("q/1", "p/1") in graph.positives
    assert ("r/1", "p/1") in graph.negatives


def test_dependency_graph_classification(tmp_path: Path) -> None:
    """Test input, output and auxiliary classification in the graph."""
    file_path = tmp_path / "test.lp"
    file_path.write_text(
        """
    output_pred(X) :- input_pred(X).
    internal_calc(X) :- input_pred(X).
    #show output_pred/1.
    """,
        encoding="utf-8",
    )

    documents = load_documents([file_path])
    context = RenderContext(_documents=documents, options=ASPOptions())
    graph = context.dependency_graph

    assert "input_pred/1" in graph.inputs
    assert "output_pred/1" in graph.outputs
    assert "internal_calc/1" in graph.auxiliaries
