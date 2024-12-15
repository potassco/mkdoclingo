"""
Module containing the handler for ASP files.
"""

from pathlib import Path
from typing import Any

from mkdocstrings.handlers.base import BaseHandler

from mkdocstrings_handlers.asp.document import Document


class ASPHandler(BaseHandler):
    """MKDocStrings handler for ASP files."""

    def __init__(
        self,
        theme: str = "material",
        config_file_path: str | None = None,
        paths: list[str] | None = None,
        locale: str = "en",
        load_external_modules: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the handler.

        Args:
            theme: The theme to use for the handler.
            config_file_path: The path to the configuration file.
            paths: A list of paths to search for ASP files.
            locale: The locale to use for the handler.
            load_external_modules: Whether to load external modules.
            **kwargs: Keyword arguments.
        """
        super().__init__("asp", theme)

    def collect(self, identifier: str, config: dict) -> dict | None:
        """
        Collect data from ASP files.

        This function will be called for all markdown files annotated with '::: some/path/to/file.lp'.

        Args:
            identifier: The identifier used in the annotation.
            config: The configuration dictionary.

        Returns:
            The collected data as a dictionary.
        """

        # All identifiers that are not valid paths to an ASP file should be ignored
        # path = identifier

        # if not path.endswith(".lp"):
        #     return None

        # if not os.path.exists(path):
        #     return None

        path = Path(identifier)
        if path.suffix != ".lp" or not path.is_file():
            return None

        # Read ASP file
        with open(path, "r") as f:
            content = f.read()

        document = Document.new(path, content)

        data = {
            "title": document.title,
            "encoding": document.content,
        }

        return data

    def render(self, data: dict, config: dict):
        """
        Render the collected data to html.

        This function will be called for all `data` collected by the collect function.

        Args:
            data: The data collected by the collect function.
            config: The configuration dictionary.

        Returns:
            The rendered data as a string
        """

        if data is None:
            return None

        # Get and render the documentation template
        template = self.env.get_template("documentation.html.jinja")
        return template.render(data)
