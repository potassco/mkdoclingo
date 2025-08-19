"""
Module containing the handler for ASP files.
"""

from collections import deque
from pathlib import Path

from markupsafe import Markup
from mkdocstrings import BaseHandler, HeadingShiftingTreeprocessor

from mkdocstrings_handlers.asp.document import Document
from mkdocstrings_handlers.asp.features.dependency_graph import DependencyGraph
from mkdocstrings_handlers.asp.features.encoding_info import EncodingInfo
from mkdocstrings_handlers.asp.features.predicate_info import PredicateInfo
from mkdocstrings_handlers.asp.semantics.document_parser import DocumentParser
from mkdocstrings_handlers.asp.tree_sitter.parser import ASPParser

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Use tomli for Python < 3.11

with open("pyproject.toml", "rb") as f:
    project_data = tomllib.load(f)

import logging

log = logging.getLogger(__name__)


class ASPHandler(BaseHandler):
    """MKDocStrings handler for ASP files."""

    handler = "asp"
    domain = "asp"
    name = "asp"

    # Only *extras* you want on top of mkdocstrings defaults (don’t include "autorefs" here)
    EXTRA_MDX = [
        "admonition",
        "def_list",
        "toc",
        "pymdownx.details",
        "pymdownx.superfences",
    ]

    EXTRA_MDX_CONFIG = {
        "toc": {"permalink": True},
        # If Material icons like :material-table: stop rendering, uncomment below:
        # "pymdownx.emoji": {
        #     "emoji_index": "materialx.emoji.twemoji",
        #     "emoji_generator": "materialx.emoji.to_svg",
        # },
    }

    DEFUALT_CONFIG = {
        "start_level": 1,
        "encodings": {"source": False, "git_link": False},
        "glossary": {
            "include_undocumented": True,
            "include_hidden": True,
            "include_references": True,
            "include_navigation": True,
        },
        "predicate_table": {"include_undocumented": True, "include_hidden": True},
        "dependency_graph": {"custome": True},
    }

    DEFAULT_OPTIONS = {
        "show_symbol_type_heading": True,
        "show_symbol_type_toc": True,
        "show_signature_annotations": True,
        "signature_cross_references": True,
        "show_source": False,
        "extra": {
            "show_inherited_detail": True,
            "show_inherited_detail_toc": True,
            "show_inherited_detail_tree": True,
        },
    }

    def __init__(self, theme: str = "material", **kwargs):
        mdx = kwargs.pop("mdx", list(self.EXTRA_MDX))
        mdx_config = kwargs.pop("mdx_config", dict(self.EXTRA_MDX_CONFIG))

        try:
            from mkdocs_autorefs.extension import AutorefsExtension

            mdx.append(AutorefsExtension())
        except ImportError:
            pass

        super().__init__(theme=theme, mdx=mdx, mdx_config=mdx_config, **kwargs)

        self.env.filters["convert_markdown_simple"] = self.do_convert_markdown_simple

    def get_options(self, config=None, **kwargs):
        """Return the options for this handler, merging defaults and user-provided options."""
        user_options = kwargs.get("options", {})
        merged = dict(self.DEFAULT_OPTIONS)
        merged.update(user_options)
        return merged

    def do_convert_markdown_simple(
        self,
        text: str,
        heading_level: int,
    ) -> Markup:
        """Render Markdown text without adding headers to the TOC

        Arguments:
            text: The text to convert.
            heading_level: The base heading level to start all Markdown headings from.

        Returns:
            An HTML string.
        """
        old_headings = [e for e in self._headings]
        treeprocessors = self._md.treeprocessors
        treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = heading_level  # type: ignore[attr-defined]

        try:
            md = Markup(self._md.convert(text))
        finally:
            treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = 0  # type: ignore[attr-defined]
            self._md.reset()

        self._headings = old_headings
        return md

    def parse_files(
        self, asp_parser: ASPParser, document_parser: DocumentParser, paths: list[Path]
    ) -> dict[Path, Document]:
        """
        Parse the files at the given paths and return a dictionary of documents.

        This also handles the inclusion of other files.

        Args:
            asp_parser: The ASP parser.
            document_parser: The document parser.
            paths: The paths to parse.

        Returns:
            A dictionary of documents.
        """
        parse_queue = deque(paths)
        documents: dict[Path, Document] = {}
        while parse_queue:
            path = parse_queue.popleft()
            if path.suffix != ".lp" or not path.is_file():
                continue

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = asp_parser.parse(content)
            document = document_parser.parse(Document(path, content), tree)
            documents[path] = document
            parse_queue.extend(include.path for include in document.includes if include.path not in documents)

        return documents

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

        # if identifier != "examples/my_test/base.lp":
        #     return None

        start_path = Path(identifier)
        asp_parser = ASPParser()
        document_parser = DocumentParser()

        documents: dict[Path, Document] = self.parse_files(asp_parser, document_parser, [start_path])

        data = {
            "project_name": project_data["project"]["name"],
            "project_url_tree": project_data["project"]["urls"]["Homepage"].replace(".git/", "/") + "tree/master/",
            "encodings": EncodingInfo.from_documents(documents.values()).encodings,
            "dependency_graph": DependencyGraph.from_document(documents.values()),
        }

        def get_key(x):
            key = x[1].show_status
            if x[1].show_status == 0:
                key = 3.5
            if not x[1].is_input:
                key += 0.1
            return key

        predicates = dict(
            sorted(
                PredicateInfo.from_documents(documents.values()).predicates.items(),
                key=get_key,
            )
        )
        data["predicate_info"] = predicates
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
        if len(data["encodings"]) == 0:
            log.warning("\033[93mNo encoding found for the given path. Rendering empty template\033[0m")
            return None

        if "start_level" not in config:
            config["start_level"] = self.DEFUALT_CONFIG["start_level"]

        sections = ["encodings", "predicate_table", "dependency_graph", "glossary"]
        for s in sections:
            if s in config:
                if isinstance(config[s], bool):
                    config[s] = {}
                default_encodings = self.DEFUALT_CONFIG[s]
                config[s] = {**default_encodings, **config[s]}

        # Get and render the documentation template
        template = self.env.get_template("documentation.html.jinja")
        # print("Rendering template with data:", data)
        return template.render(**data, config=config)

    def get_templates(self) -> Path:
        return Path(__file__).parent / "templates"
