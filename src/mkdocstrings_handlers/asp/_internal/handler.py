"""This module defines the ASP handler for mkdocstrings."""

# pylint: disable=too-many-positional-arguments

import copy
from pathlib import Path
from typing import Any, Mapping, Sequence, cast

from markdown import Extension
from markupsafe import Markup
from mkdocstrings import BaseHandler, HeadingShiftingTreeprocessor

from mkdocstrings_handlers.asp._internal.collect.load import load_documents
from mkdocstrings_handlers.asp._internal.config import ASPOptions
from mkdocstrings_handlers.asp._internal.domain import Document
from mkdocstrings_handlers.asp._internal.render.render_context import RenderContext


class ASPHandler(BaseHandler):
    """MKDocStrings handler for ASP files."""

    handler = "asp"
    domain = "asp"
    name = "asp"

    def __init__(
        self,
        *,
        theme: str,
        custom_templates: str | None,
        mdx: Sequence[str | Extension],
        mdx_config: Mapping[str, Any],
        tool_config: Mapping[str, Any],
        handler_config: Mapping[str, Any],
    ):
        super().__init__(theme=theme, custom_templates=custom_templates, mdx=mdx, mdx_config=mdx_config)

        self._tool_config = tool_config
        self._handler_config = handler_config

    def get_options(self, local_options: Mapping[str, Any]) -> ASPOptions:
        """
        Merge global (from mkdocs.yml) with local (from the markdown file) options.

        Args:
            local_options: Options provided in the annotation.

        Returns:
            The merged options.
        """

        options = dict(local_options)
        merged_options = copy.deepcopy(self._handler_config.get("options", {}))

        def deep_update(target: dict[str, Any], source: dict[str, Any]) -> None:
            for k, v in source.items():
                if isinstance(v, dict) and k in target and isinstance(target[k], dict):
                    # Nested dictionaries should also be merged
                    deep_update(target[k], v)
                else:
                    # Local configuration has higher priority
                    target[k] = v

        deep_update(merged_options, options)

        repo_url = self._tool_config.get("repo_url")

        if repo_url:
            merged_options["repo_url"] = repo_url

        return ASPOptions.from_mapping(merged_options)

    def collect(self, identifier: str, options: ASPOptions) -> list[Document]:
        """
        Collect data from ASP files.

        This function will be called for all markdown files annotated with '::: some/path/to/file.lp' using
        this handler.

        Args:
            identifier: The identifier (path) used in the annotation.
            options: Options provided by `get_options`.

        Returns:
            The collected data as a dictionary.
        """

        return load_documents([Path(identifier)])

    def render(self, data: list[Document], options: ASPOptions, **_kwargs: Any) -> str:
        """
        Render the collected data into a format suitable for mkdocstrings.

        Args:

            options: Options provided by `get_options`.

        Returns:
            The rendered data as a dictionary.
        """

        context = RenderContext(documents=data, options=options)

        template = self.env.get_template("documentation.html.jinja")

        return template.render(context=context)

    def update_env(self, config: Any) -> None:
        """
        Update the Jinja2 environment with custom filters.

        Args:
            config: The mkdocs config object.
        """
        self.env.filters["convert_markdown_simple"] = self.do_convert_markdown_simple

    def do_convert_markdown_simple(
        self,
        text: str,
        heading_level: int,
    ) -> Markup:
        """
        Convert the given text from Markdown to HTML based on a given
        heading level without altering existing headings or affecting future headings.

        Args:
            text: The Markdown text to convert.
            heading_level: The level to shift headings by.

        Returns:
            The converted HTML as Markup.
        """
        old_headings = list(self._headings)

        if self._md is None:
            raise RuntimeError("Markdown instance is not initialized.")

        processor = cast(HeadingShiftingTreeprocessor, self._md.treeprocessors[HeadingShiftingTreeprocessor.name])
        processor.shift_by = heading_level

        try:
            md = Markup(self._md.convert(text))
        finally:
            processor.shift_by = 0
            self._md.reset()

        self._headings = old_headings
        return md


def get_handler(
    theme: str,
    custom_templates: str | None,
    mdx: Sequence[str | Extension],
    mdx_config: Mapping[str, Any],
    tool_config: Mapping[str, Any],
    handler_config: Mapping[str, Any],
    **_kwargs: Any,
) -> ASPHandler:
    """
    Return an instance of `ASPHandler`.

    This is required by mkdocstrings to load the handler.
    """
    return ASPHandler(
        theme=theme or "material",
        custom_templates=custom_templates,
        mdx=mdx,
        mdx_config=mdx_config,
        tool_config=tool_config,
        handler_config=handler_config,
    )
