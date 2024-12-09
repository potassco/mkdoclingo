"""
Module containing the handler for ASP files.
"""

import os
from typing import Any

import markdown
from mkdocstrings.handlers.base import BaseHandler


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

    def collect(self, identifier: str, config: dict) -> dict:
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
        path = identifier

        if not path.endswith(".lp"):
            return None

        if not os.path.exists(path):
            return None

        # Collect data for the associated ASP file
        with open(path, "r") as f:
            content = f.read()

            # TODO: Implement actual data collection,
            # this is just a basic example placeholder
            encoding_data = {
                "content": content,
            }

        return encoding_data

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

        # Render the data using a Jinja2 template
        # this effectively replaces all variables in the template with the provided data
        template = self.env.get_template("example_template.html")
        first_render = template.render(data)

        # Render the result a second time to convert the markdown contained in the template to html
        # for now this is sufficient, but other projects use this function within the templates themselves
        # so this may have to be revised.
        second_render = self.do_convert_markdown(first_render, 0)

        return second_render
