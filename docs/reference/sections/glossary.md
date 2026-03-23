---
icon: "material/format-list-bulleted-square"
---

Generates a glossary with detailed information of all predicates using their predicate documentation. See the [predicate documentation](../predicate-docs.md) section for more details.

Each predicate generates a section in the TOC.

Each predicate section includes the references for each file where the predicate was used.

!!! example

    === ":material-palette-outline: Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                glossary: true
                start_level: 3

    === ":material-code-block-tags: Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                glossary: true
                start_level: 3
        ```



## Configuration options

The option `glossary` can be further customized with the following options:

- `include_references` Boolean indicating if each predicate documentations should include a section with the references. Defaults to True.
- `include_navigation` Boolean indicating if each predicate should generate a navigation entry displayed in the menu. Defaults to True.

Predicate inclusion/exclusion (e.g. hidden or undocumented predicates) is configured globally via `predicate_info`.


!!! example


    === ":material-palette-outline: Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                glossary:
                    include_references: false
                predicate_info:
                    include_undocumented: false
                start_level: 3

    === ":material-code-block-tags: Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                glossary:
                    include_references: false
                predicate_info:
                    include_undocumented: false
                start_level: 3
        ```
