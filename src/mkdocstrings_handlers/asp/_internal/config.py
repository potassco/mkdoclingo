"""This module defines the configuration options for the ASP handler."""

from __future__ import annotations

from typing import Any, Mapping

from pydantic import BaseModel, Field, ValidationError, model_validator


class FeatureConfig(BaseModel):
    """Base class for feature configuration."""

    enabled: bool = False
    """Whether this feature is enabled."""


class EncodingOptions(FeatureConfig):
    """Options for encoding outputs."""

    source: bool = False
    """ Whether to encode source code blocks. """
    git_link: bool = False
    """
    Whether to include git links.

    This requires a repository link to be set.
    """


class GlossaryOptions(FeatureConfig):
    """Options for glossary generation."""

    include_undocumented: bool = True
    """ Whether to include undocumented predicates in the glossary. """
    include_hidden: bool = True
    """ Whether to include hidden predicates in the glossary. """
    include_references: bool = True
    """ Whether to include references in the glossary. """
    include_navigation: bool = True
    """ Whether to include navigation links in the glossary. """


class PredicateTableOptions(FeatureConfig):
    """Options for predicate table generation."""

    include_undocumented: bool = True
    """ Whether to include undocumented predicates in the predicate table. """
    include_hidden: bool = True
    """ Whether to include hidden predicates in the predicate table. """


class DependencyGraphOptions(FeatureConfig):
    """Options for dependency graph generation."""


class ASPOptions(BaseModel):
    """
    Main configuration with Runtime Validation.
    """

    repo_url: str | None = None
    start_level: int = Field(default=1, ge=1)
    encodings: EncodingOptions = Field(default_factory=EncodingOptions)
    glossary: GlossaryOptions = Field(default_factory=GlossaryOptions)
    predicate_table: PredicateTableOptions = Field(default_factory=PredicateTableOptions)
    dependency_graph: DependencyGraphOptions = Field(default_factory=DependencyGraphOptions)

    @model_validator(mode="before")
    @classmethod
    def handle_boolean_shortcuts(cls, data: Any) -> Any:
        """
        Allow boolean shortcuts in the configuration.

        This allows the user to either enable a feature using its defaults
        (by setting it to True) or disable it entirely (by setting it to False) without
        using the `enabled` field.

        Args:
            data: The input data to validate.

        Returns:
            The modified data with boolean shortcuts handled.
        """
        if not isinstance(data, dict):
            return data

        features = [
            "encodings",
            "glossary",
            "predicate_table",
            "dependency_graph",
        ]

        for feature in features:
            if feature in data:
                value = data[feature]

                if value is True:
                    data[feature] = {"enabled": True}

                elif value is False:
                    data[feature] = {"enabled": False}

                elif isinstance(value, dict):
                    if "enabled" not in value:
                        value["enabled"] = True
        return data

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> ASPOptions:
        """
        Create an ASPOptions instance from a dictionary.

        Args:
            data: The input data to create the instance from.

        Returns:
            An instance of ASPOptions.
        """
        try:
            return cls.model_validate(data)
        except ValidationError as e:
            print(f"Configuration Error in mkdocs.yml: {e}")
            return cls()
