---
icon: "material/graphql"
---


Generates a dependency graph between predicates. Input predicates are shown purple and shown predicates in green.

!!! example

    === ":material-palette-outline: Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                dependency_graph: true
                start_level: 3

    === ":material-code-block-tags: Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                dependency_graph: true
                start_level: 3
        ```




## Configuration options

<!-- - `include-undocumented` Boolean indicating if predicates that have no docstring should be included. Defaults to True. -->
