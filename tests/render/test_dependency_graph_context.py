"""Tests for the dependency graph context in ASP rendering."""

from typing import Callable

from mkdocstrings_handlers.asp._internal.render.render_context import RenderContext


def test_dependency_graph_structure(render_context: Callable[[str], RenderContext]) -> None:
    """Test that the dependency graph context is built correctly."""

    context = render_context("p(X) :- q(X), not r(X).")

    graph = context.dependency_graph

    assert "p/1" in graph.all
    assert "q/1" in graph.all
    assert "r/1" in graph.all
    assert ("q/1", "p/1") in graph.positives
    assert ("r/1", "p/1") in graph.negatives


def test_dependency_graph_classification(render_context: Callable[[str], RenderContext]) -> None:
    """Test input, output and auxiliary classification in the graph."""

    context = render_context(
        """
    output_pred(X) :- input_pred(X).
    internal_calc(X) :- input_pred(X).
    #show output_pred/1.
    """
    )
    graph = context.dependency_graph

    assert "input_pred/1" in graph.inputs
    assert "output_pred/1" in graph.outputs
    assert "internal_calc/1" in graph.auxiliaries
