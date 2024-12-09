"""Entry point of the mkdocstrings handler module."""

from .handler import ASPHandler


def get_handler(**kwargs):
    """
    Return an instance of the ASPHandler class.

    This is required by mkdocstrings to load the handler.
    """

    return ASPHandler(**kwargs)
