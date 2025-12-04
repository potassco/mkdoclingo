from pathlib import Path

from mkdocstrings import BaseHandler
from mkdocstrings_handlers.asp._internal.collect.collectors import collect_from_files
from mkdocstrings_handlers.asp._internal.config import ASPOptions


class ASPHandler(BaseHandler):
    """MKDocStrings handler for ASP files."""

    handler = "asp"
    domain = "asp"
    name = "asp"

    def get_options(self, local_options: dict) -> dict:
        """
        Merge global defaults with local options (from the markdown file).

        Args:
            local_options: Options provided in the annotation.

        Returns:
            Merged options dictionary.
        """
        return ASPOptions.from_dict(local_options)

    def collect(self, identifier: str, options: ASPOptions) -> dict:
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

        collect_from_files([Path(identifier)])

        return {"bla": 1}

    def render(self, data: dict, options: ASPOptions) -> dict:
        """
        Render the collected data into a format suitable for mkdocstrings.

        Args:
            data: The collected data from `collect`.
            options: Options provided by `get_options`.

        Returns:
            The rendered data as a dictionary.
        """


def get_handler(theme: str, handler_config: dict, tool_config: dict, **kwargs):
    """
    Return an instance of `ASPHandler`.

    This is required by mkdocstrings to load the handler.
    """
    return ASPHandler(theme=theme or "material", **kwargs)
