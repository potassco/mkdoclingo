from __future__ import annotations

from typing import Any, Dict, Mapping, Type

from pydantic import BaseModel, Field, ValidationError, model_validator


class EncodingOptions(BaseModel):
    source: bool = False
    git_link: bool = False


class GlossaryOptions(BaseModel):
    include_undocumented: bool = True
    include_hidden: bool = True
    include_references: bool = True
    include_navigation: bool = True


class PredicateTableOptions(BaseModel):
    include_undocumented: bool = True
    include_hidden: bool = True


class DependencyGraphOptions(BaseModel):
    custom: bool = True


class ASPOptions(BaseModel):
    """
    Main configuration with Runtime Validation.
    """

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
        (by setting it to True) or disable it entirely (by setting it to False).

        Args:
            data: The input data to validate.

        Returns:
            The modified data with boolean shortcuts handled.
        """
        if not isinstance(data, dict):
            return data

        section_map: Dict[str, Type[BaseModel]] = {
            "encodings": EncodingOptions,
            "glossary": GlossaryOptions,
            "predicate_table": PredicateTableOptions,
            "dependency_graph": DependencyGraphOptions,
        }

        for field_name, model_cls in section_map.items():
            if field_name in data:
                value = data[field_name]

                if value is True:
                    data[field_name] = {}

                elif value is False:
                    disabled_config = {k: False for k in model_cls.model_fields.keys()}
                    data[field_name] = disabled_config

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
