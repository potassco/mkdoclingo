"""Tests for the ASPOptions configuration class."""

from pytest import CaptureFixture

from mkdocstrings_handlers.asp._internal.config import ASPOptions


def test_from_mapping_valid() -> None:
    """Test loading from a standard dictionary."""

    data = {"start_level": 2, "encodings": {"source": True}, "glossary": {"include_hidden": False}}
    options = ASPOptions.from_mapping(data)

    assert options.start_level == 2
    assert options.dependency_graph.enabled is False
    assert options.predicate_table.enabled is False
    assert options.encodings.enabled is True
    assert options.encodings.source is True
    assert options.encodings.git_link is False
    assert options.glossary.enabled is True
    assert options.glossary.include_hidden is False
    assert options.glossary.include_undocumented is True


def test_validation_error_handling(capsys: CaptureFixture[str]) -> None:
    """
    Test that validation errors are caught and printed (fallback to defaults).

    We test it with start_level being less than 1 and expect:
    - An error message to be printed.
    - The default configuration to be used.
    """

    data = {"start_level": 0}

    options = ASPOptions.from_mapping(data)
    assert options.start_level == 1
    captured = capsys.readouterr()
    assert "Configuration Error" in captured.out


def test_validation_error_on_non_dict_input(capsys: CaptureFixture[str]) -> None:
    """
    Test that pydantic raises a ValidationError when input is not a dict.
    """

    invalid_input = 123
    options = ASPOptions.from_mapping(invalid_input)  # type: ignore
    assert options == ASPOptions()

    captured = capsys.readouterr()
    assert "Configuration Error" in captured.out


def test_boolean_shortcut_true() -> None:
    """Test that setting a section to True enables defaults."""

    data = {"encodings": True, "glossary": True}
    options = ASPOptions.model_validate(data)

    assert options.encodings.enabled is True
    assert options.encodings.source is False
    assert options.glossary.include_undocumented is True


def test_boolean_shortcut_false() -> None:
    """Test that setting a section to False disables everything."""

    data = {"glossary": False, "dependency_graph": False}
    options = ASPOptions.model_validate(data)

    assert options.glossary.enabled is False
