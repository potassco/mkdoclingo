from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mkdocstrings_handlers.asp._internal.semantics.directives.include import Include


@dataclass
class Document:
    path: Path
    content: str
    includes: list[Include] = field(default_factory=list)
