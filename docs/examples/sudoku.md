---
icon: material/grid
---

# Sudoku

:material-eye-off:
:octicons-eye-closed-16:
We showcase how to generate documentation for each available option.

!!! tip

    Ideally all options are activated in the same statement to avoid
    analyzing the files multiple times.


## :material-file-document-arrow-right: Generating *"Encodings"*

Generates a section with the encodings used

!!! example "Encodings"

    === "Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                encodings:
                    source: true
                start_level: 2

    === "Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                encodings: true
                start_level: 2
        ```

## :material-file-document-arrow-right: Generating *"Predicates table"*

Generates a summary of the predicates used in the encoding and all included encodings.

!!! example "Predicates table"

    === "Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                predicate_table: true
                start_level: 2


    === "Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                predicate_table: true
                start_level: 2
        ```

## :material-file-document-arrow-right: Generating *"Dependency graph"*

Generates a dependency graph between predicates

!!! example "Dependency Graph"

    === "Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                dependency_graph: true
                start_level: 2


    === "Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                dependency_graph: true
                start_level: 2
        ```


## :material-file-document-arrow-right: Generating *"Glossary"*

Generates a glossary with detailed information of all predicates including references to files where they are defined and used.

!!! example "Glossary"

    === "Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                glossary: true
                start_level: 2


    === "Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                glossary: true
                start_level: 2
        ```
