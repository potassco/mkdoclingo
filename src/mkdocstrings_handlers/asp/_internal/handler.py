from pathlib import Path
from typing import Any, Mapping

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

    def get_options(self, local_options: Mapping[str, Any]) -> ASPOptions:
        """
        Merge global defaults with local options (from the markdown file).

        Args:
            local_options: Options provided in the annotation.

        Returns:
            The merged options.
        """
        return ASPOptions.from_mapping(local_options)

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

    def render(self, data: list[Document], options: ASPOptions, **kwargs: Any) -> str:
        """
        Render the collected data into a format suitable for mkdocstrings.

        Args:

            options: Options provided by `get_options`.

        Returns:
            The rendered data as a dictionary.
        """

        context = RenderContext(_documents=data, options=options)

        try:
            template = self.env.get_template("documentation.html.jinja")
        except Exception:
            return "<p>Template not found.</p>"

        # try:
        return template.render(context=context)
        # except Exception:

        #     return "<p>Rendering failed.</p>"

    def update_env(self, config: Any) -> None:
        self.env.filters["convert_markdown_simple"] = self.do_convert_markdown_simple

    def do_convert_markdown_simple(
        self,
        text: str,
        heading_level: int,
    ) -> Markup:
        old_headings = [e for e in self._headings]

        if self._md is None:
            raise RuntimeError("Markdown instance is not initialized.")

        treeprocessors = self._md.treeprocessors
        treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = heading_level

        try:
            md = Markup(self._md.convert(text))
        finally:
            treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = 0
            self._md.reset()

        self._headings = old_headings
        return md


def get_handler(theme: str, handler_config: dict[str, Any], tool_config: dict[str, Any], **kwargs: Any) -> ASPHandler:
    """
    Return an instance of `ASPHandler`.

    This is required by mkdocstrings to load the handler.
    """
    return ASPHandler(theme=theme or "material", **kwargs)
