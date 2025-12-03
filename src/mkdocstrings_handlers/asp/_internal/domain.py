from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Include:
    """An include directive in an ASP document."""

    path: Path
    """ The path of the included file."""


@dataclass
class Document:
    path: Path
    content: str
    includes: list[Include] = field(default_factory=list)
