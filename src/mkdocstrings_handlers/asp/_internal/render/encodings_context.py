"""This module defines the encoding context for rendering."""

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import PurePath, PureWindowsPath
from urllib.parse import urljoin

from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.domain import (
    Document,
    Include,
    LocatedContent,
    Statement,
)


class BlockType(Enum):
    """The type of an encoding block."""

    CODE = auto()
    """ Code block. """
    MARKDOWN = auto()
    """ Markdown block. """


@dataclass
class EncodingBlock:
    """A block within an encoding, either code or markdown."""

    type: BlockType
    """ The type of the block. """
    content: str
    """ The content of the block. """


@dataclass
class EncodingInfo:
    """Information about an encoding file."""

    repository_url: str | None
    """ The repository URL of the encoding, if available. """
    path: str
    """ The path to the encoding file. """
    source: str
    """ The content as plain source code"""
    blocks: list[EncodingBlock] = field(default_factory=list)
    """ The content split into blocks. """

    @property
    def name(self) -> str:
        """The name of the encoding, derived from the path."""
        return PurePath(self.path).name if PurePath(self.path).name != self.path else PureWindowsPath(self.path).name


@dataclass
class EncodingContext:
    """The encoding context containing all encoding infos."""

    entries: list[EncodingInfo] = field(default_factory=list)
    """ The list of encoding infos. """


def get_encoding_context(documents: list[Document], options: ASPOptions) -> EncodingContext:
    """
    Build the encoding context from the given documents.

    Args:
        documents: The list of Document objects representing ASP encodings.

    Returns:
        The constructed EncodingContext.
    """
    encodings = []

    for document in documents:
        ordered_elements: list[LocatedContent] = list(document.includes)

        ordered_elements.extend(document.statements)

        ordered_elements.extend(document.block_comments)

        for line_comment in document.line_comments:
            content = line_comment.content.strip()
            if content.startswith("%"):
                continue
            ordered_elements.append(line_comment)

        ordered_elements.sort(key=lambda element: element.row)

        repository_url = None
        if options.repo_url:
            repository_url = urljoin(
                urljoin(options.repo_url.rstrip("/") + "/", "tree/master/"), str(document.path.as_posix()).lstrip("/")
            )

        encoding = EncodingInfo(path=str(document.path), source=document.content, repository_url=repository_url)

        current_block_content = ""
        current_block_type = BlockType.MARKDOWN

        for element in ordered_elements:
            if isinstance(element, (Statement, Include)):
                if current_block_type != BlockType.CODE:
                    if current_block_content:
                        encoding.blocks.append(
                            EncodingBlock(
                                type=current_block_type,
                                content=current_block_content,
                            )
                        )
                    current_block_content = ""
                    current_block_type = BlockType.CODE

                current_block_content += element.content + "\n"

            else:
                if current_block_type != BlockType.MARKDOWN:
                    if current_block_content:
                        encoding.blocks.append(
                            EncodingBlock(
                                type=current_block_type,
                                content=current_block_content,
                            )
                        )
                    current_block_content = ""
                    current_block_type = BlockType.MARKDOWN

                current_block_content += element.content + "\n"

        if current_block_content:
            encoding.blocks.append(
                EncodingBlock(
                    type=current_block_type,
                    content=current_block_content,
                )
            )

        encodings.append(encoding)

    return EncodingContext(entries=encodings)
