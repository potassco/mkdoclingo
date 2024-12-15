from mkdocstrings_handlers.asp.document import Document


def get_dependency_graph(document: Document) -> dict:
    """
    Get the dependency graph of the given ASP document.

    Args:
        document: The ASP document.

    Returns:
        The dependency graph as a dictionary.
    """
    data = {}

    for statement in document.statements:
        for provided in statement.provided_literals:
            lit_id = f"{provided.identifier}/{provided.arity}"
            positive = set(
                map(lambda x: f"{x.identifier}/{x.arity}", filter(lambda x: not x.negation, statement.needed_literals))
            )
            negative = set(
                map(lambda x: f"{x.identifier}/{x.arity}", filter(lambda x: x.negation, statement.needed_literals))
            )
            if lit_id not in data:
                data[lit_id] = {"positive": set(), "negative": set()}

            data[lit_id]["positive"].update(positive)
            data[lit_id]["negative"].update(negative)

    return data
