from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict

from mkdocstrings_handlers.asp.document import Document
from mkdocstrings_handlers.asp.semantics.predicate import Predicate, ShowStatus


@dataclass
class PredicateInfo:
    predicates: Dict[str, Predicate] = field(default_factory=OrderedDict)
    """Dictionary of predicates with their signatures as keys."""

    @staticmethod
    def from_documents(documents: dict[Document]) -> PredicateInfo:
        """
        Create a predicate list from a list of documents.

        Args:
            documents: The documents to create the predicate list from.

        Returns:
            The predicate list.
        """
        predicates: dict[str, Predicate] = {}
        disable_default_show = False

        # If any document has disable_default_show set to True
        # set it to True for all predicates
        for document in documents:
            disable_default_show |= document.disable_default_show

        # Collect all predicates with updated show status
        for document in documents:
            for predicate in document.predicates.values():
                signatuture = predicate.signature
                if signatuture not in predicates:
                    predicates[signatuture] = predicate

                if disable_default_show:
                    predicates[signatuture].update_show_status(ShowStatus.HIDDEN)

                predicates[signatuture].update_show_status(predicate.show_status)
                if predicates[signatuture].documentation is None:
                    predicates[signatuture].documentation = predicate.documentation

        # Create an ordered dictionary sorted by signature
        sorted_predicates = OrderedDict(sorted(predicates.items(), key=lambda x: x[0]))

        return PredicateInfo(sorted_predicates)
