# Development

To improve code quality, we use [nox] to run linters, type checkers, unit
tests, documentation and more. We recommend installing nox using [pipx] to have
it available globally.

```bash
# install
python -m pip install pipx
python -m pipx install nox

# run all sessions
nox

# list all sessions
nox -l

# run individual session
nox -s session_name

# run individual session (reuse install)
nox -Rs session_name
```

Note that the nox sessions create [editable] installs. In case there are
issues, try recreating environments by dropping the `-R` option. If your
project is incompatible with editable installs, adjust the `noxfile.py` to
disable them.

We also provide a [pre-commit][pre] config to autoformat code upon commits. It
can be set up using the following commands:

```bash
python -m pipx install pre-commit
pre-commit install
```

## Code structure

```text
src/mkdocstrings_handlers/asp/
└── _internal/
    ├── collect/                        # Parsing logic (Input)
    │   ├── queries/                    # *.scm files with tree-sitter queries
    │   ├── extractors.py               # Extract data from nodes using queries
    │   ├── load.py                     # File loading and processing loop
    │   └── syntax.py                   # Query wrappers and node definitions
    ├── render/                         # View model generation (Processing)
    │   ├── render_context.py           # Main rendering context
    │   ├── dependency_graph_context.py # Dependency graph context
    │   ├── encodings_context.py        # Encodings context
    │   ├── glossary_context.py         # Glossary context
    │   └── predicate_table_context.py  # Predicate table context
    ├── config.py                       # Configuration options (using Pydantic)
    ├── domain.py                       # Domain models (Document, Statement, etc.)
    └── handler.py                      # MkDocstrings handler entry point
```

[editable]: https://setuptools.pypa.io/en/latest/userguide/development_mode.html
[nox]: https://nox.thea.codes/en/stable/index.html
[pipx]: https://pypa.github.io/pipx/
[pre]: https://pre-commit.com/
