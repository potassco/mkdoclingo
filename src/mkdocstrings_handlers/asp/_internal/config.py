from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field, ValidationError


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ASPOptions:
        try:
            return cls.model_validate(data)
        except ValidationError as e:
            print(f"Configuration Error in mkdocs.yml: {e}")
            return cls()
