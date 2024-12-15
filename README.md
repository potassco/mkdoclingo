# mkdoclingo

## Installation

To install the project, run

```bash
pip install .
```

## Usage

Run the following for basic usage information:

```bash
mkdoclingo -h
```

To generate and open the documentation, run

```bash
nox -s doc -- serve
```

Instructions to install and use `nox` can be found in
[DEVELOPMENT.md](./DEVELOPMENT.md)

## How to use the Handler

1. Add this project to your dependencies

1. Add handler to `mkdocs.yml`

   ```yml
   plugins:
   - mkdocstrings:
       handlers:
           asp:
           paths: [encodings]
   ```

1. You may now use mkdocstrings identifiers like so:

   ```
   ::: some/path/to/encoding.lp
       handler: asp
   ```

## Options

The output is customizable via options.

For example:

```
::: some/path/to/encoding.lp
    handler: asp
    options:
        source: true
```

shows the source code of the corresponding encoding.

### Currently available options

- `source`: Source code of the encoding
- `dependency_graph`: Predicate dependency graph of the encoding
- `glossary`: Sorted information about predicates
