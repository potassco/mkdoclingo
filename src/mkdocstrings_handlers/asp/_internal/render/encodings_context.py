from dataclasses import dataclass, field
from enum import Enum, auto

from mkdocstrings_handlers.asp._internal.domain import Document, Statement


class BlockType(Enum):
    CODE = auto()
    MARKDOWN = auto()


@dataclass
class EncodingBlock:
    type: BlockType
    content: str


@dataclass
class EncodingInfo:
    path: str
    source: str
    blocks: list[EncodingBlock] = field(default_factory=list)


@dataclass
class EncodingContext:
    encodings: list[EncodingInfo] = field(default_factory=list)


def get_encoding_context(documents: list[Document]) -> EncodingContext:
    encodings = []

    for document in documents:
        ordered_elements = document.statements + document.line_comments + document.block_comments
        ordered_elements.sort(key=lambda element: element.row)

        encoding = EncodingInfo(path=str(document.path), source=document.content)

        current_block_content = ""
        current_block_type = BlockType.MARKDOWN

        for element in ordered_elements:
            if isinstance(element, Statement):
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

    return EncodingContext(encodings=encodings)
