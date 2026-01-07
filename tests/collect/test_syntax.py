"""Tests for the syntax module dealing with tree sitter queries from scm files."""

from pathlib import Path
from unittest.mock import patch

import pytest

from mkdocstrings_handlers.asp._internal.collect.syntax import AspQuery


def test_asp_query_success(tmp_path: Path) -> None:
    """Test that AspQuery correctly reads a file and initializes a Query object."""

    file_name = "test.scm"
    file_content = """
    (rule
        (literal) @literal_capture
    ) @rule_capture"""
    file = tmp_path / file_name
    file.write_text(file_content, encoding="utf-8")

    target_module = "mkdocstrings_handlers.asp._internal.collect.syntax"

    with patch(f"{target_module}._QUERY_DIR", tmp_path):
        asp_query = AspQuery(file_name)
        assert asp_query.query.capture_count == 2  # type: ignore[comparison-overlap]
        assert asp_query.query.capture_name(0) == "literal_capture"
        assert asp_query.query.capture_name(1) == "rule_capture"


def test_asp_query_file_not_found() -> None:
    """Test that a missing SCM file raises a RuntimeError."""

    query_wrapper = AspQuery("non_existent_file.scm")

    with pytest.raises(RuntimeError) as exc_info:
        _ = query_wrapper.query

    assert "Missing SCM file: non_existent_file.scm" in str(exc_info.value)
