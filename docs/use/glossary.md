---
icon: "material/format-list-bulleted-square"
---

Generates a glossary with detailed information of all predicates using their predicate documentation. See the [predicate documentation](#predicate-documentation) section for more details.

Each predicate generates a section in the TOC.

Each predicate section includes the references for each file where the predicate was used.

!!! example

    === "Usage"

        ```
        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                glossary: true
                start_level: 3
        ```

    === "Output"

        ::: examples/sudoku/encoding.lp
            handler: asp
            options:
                glossary: true
                start_level: 3


## Predicate documentation

TODO


## Configuration options

- `ignore-undocumented` TODO
- `ignore-hidden` TODO
- `include-references` TODO
- `ignore-includes` Boolean indication that the included files should not considered TODO
